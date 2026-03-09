"""
routes/api.py
=============
Blueprint untuk semua endpoint API (JSON).

Endpoint publik (tanpa login — untuk ESP8266):
  POST /api/sensor              → terima data sensor dari ESP8266

Endpoint dengan login:
  GET  /api/sensor              → ambil data sensor (dengan filter & pagination)
  GET  /api/sensor/latest       → data sensor terbaru
  GET  /api/export/csv          → export data ke file CSV
  GET  /api/servo/status        → status servo saat ini

Endpoint admin only:
  POST   /api/servo/open        → putar servo ke 180° (nyala/buka)
  POST   /api/servo/close       → putar servo ke 0° (mati/tutup)
  POST   /api/servo/angle       → putar servo ke sudut tertentu (?angle=N)
  DELETE /api/sensor/clear      → hapus semua data sensor
"""

import csv
import io
import requests as req_lib

from flask    import Blueprint, request, jsonify, Response, session
from datetime import datetime

from models.database   import sensor_insert, sensor_fetch, sensor_count, sensor_clear
from models.decorators import api_login_required, api_admin_required

api_bp = Blueprint('api', __name__)

# ── State bersama (dibaca juga oleh dashboard.py) ────────────
sensor_buffer: list = []   # cache 100 data terakhir di memori
MAX_BUFFER = 100
esp_ip: str | None = None  # IP ESP8266 yang terakhir mengirim data


# ============================================================
# TERIMA DATA SENSOR (dari ESP8266, tanpa auth)
# ============================================================

@api_bp.route('/api/sensor', methods=['POST'])
def receive_sensor():
    """
    ESP8266 mengirim data setiap interval via POST JSON:
    {
      "temperature": 28.5,
      "humidity": 65.2,
      "servo_angle": 0,       ← opsional
      "device_id": "esp-01",  ← opsional
      "esp_ip": "192.168.x.x" ← opsional, untuk menyimpan IP
    }
    """
    global esp_ip

    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Content-Type harus application/json'}), 400

    data = request.get_json()

    # Validasi field wajib
    for field in ['temperature', 'humidity']:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'Field {field} tidak ada'}), 400

    # Simpan IP ESP8266 jika dikirimkan
    if data.get('esp_ip'):
        esp_ip = data['esp_ip']

    # Buat entry dan simpan ke DB + buffer
    entry = {
        'temperature': float(data['temperature']),
        'humidity':    float(data['humidity']),
        'device_id':   data.get('device_id', 'unknown'),
        'servo_angle': int(data.get('servo_angle', 0)),
        'timestamp':   datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ip':          request.remote_addr,
    }
    sensor_insert(entry)

    sensor_buffer.append(entry)
    if len(sensor_buffer) > MAX_BUFFER:
        sensor_buffer.pop(0)  # buang data tertua jika buffer penuh

    print(f"[DATA] {entry['timestamp']} | {entry['temperature']}°C | {entry['humidity']}% | servo:{entry['servo_angle']}°")
    return jsonify({'status': 'success', 'message': 'Tersimpan ke DB'}), 200


# ============================================================
# BACA DATA SENSOR
# ============================================================

@api_bp.route('/api/sensor', methods=['GET'])
@api_login_required
def get_sensor():
    """Ambil banyak baris data sensor dengan pagination & filter tanggal."""
    rows = sensor_fetch(
        request.args.get('limit',     50,   type=int),
        request.args.get('offset',    0,    type=int),
        request.args.get('date_from') or None,
        request.args.get('date_to')   or None,
    )
    return jsonify({
        'status': 'success',
        'count':  len(rows),
        'total':  sensor_count(),
        'data':   rows,
    })


@api_bp.route('/api/sensor/latest', methods=['GET'])
@api_login_required
def get_latest():
    """Ambil hanya 1 baris data sensor terbaru."""
    rows = sensor_fetch(limit=1)
    if not rows:
        return jsonify({'status': 'error', 'message': 'Belum ada data'}), 404
    return jsonify({'status': 'success', 'data': rows[0]})


@api_bp.route('/api/sensor/clear', methods=['DELETE'])
@api_admin_required
def clear_data():
    """Hapus semua data sensor dari DB dan buffer (admin only)."""
    sensor_clear()
    sensor_buffer.clear()
    return jsonify({'status': 'success', 'message': 'Database sensor dikosongkan'})


# ============================================================
# EXPORT CSV
# ============================================================

@api_bp.route('/api/export/csv')
@api_login_required
def export_csv():
    """
    Unduh semua data sensor sebagai file .csv.
    Mendukung filter tanggal yang sama dengan halaman dashboard.
    """
    date_from = request.args.get('date_from') or None
    date_to   = request.args.get('date_to')   or None
    rows      = sensor_fetch(limit=999_999, offset=0, date_from=date_from, date_to=date_to)

    out = io.StringIO()
    w   = csv.DictWriter(out, fieldnames=['id','timestamp','temperature','humidity','servo_angle','device_id','ip'])
    w.writeheader()
    w.writerows(rows)

    fname = f"sensor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        out.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={fname}'}
    )


# ============================================================
# KONTROL SERVO (komunikasi ke ESP8266)
# ============================================================

def _send_to_esp(endpoint: str, params=None):
    """
    Helper: kirim HTTP GET ke ESP8266.
    Return (dict_response, status_code).
    """
    if not esp_ip:
        return {'status': 'error', 'message': 'IP ESP8266 belum diketahui.'}, 503
    try:
        r = req_lib.get(f"http://{esp_ip}{endpoint}", params=params, timeout=5)
        return r.json(), r.status_code
    except req_lib.exceptions.Timeout:
        return {'status': 'error', 'message': 'ESP8266 timeout (5s)'}, 504
    except req_lib.exceptions.ConnectionError:
        return {'status': 'error', 'message': f'Tidak bisa terhubung ke {esp_ip}'}, 503
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@api_bp.route('/api/servo/open', methods=['POST'])

def servo_open():
    """Kirim perintah ke ESP8266 untuk memutar servo ke 180° (buka/nyala)."""
    res, code = _send_to_esp('/servo/open')
    if isinstance(res, dict) and res.get('status') == 'success':
        res['angle'] = 180
    return jsonify(res), code


@api_bp.route('/api/servo/close', methods=['POST'])

def servo_close():
    """Kirim perintah ke ESP8266 untuk memutar servo ke 0° (tutup/mati)."""
    res, code = _send_to_esp('/servo/close')
    if isinstance(res, dict) and res.get('status') == 'success':
        res['angle'] = 0
    return jsonify(res), code


@api_bp.route('/api/servo/angle', methods=['POST'])

def servo_set_angle():
    """Kirim sudut kustom ke ESP8266 (?angle=0-180)."""
    angle     = request.args.get('angle', 180)
    res, code = _send_to_esp('/servo/angle', params={'angle': angle})
    if isinstance(res, dict) and res.get('status') == 'success':
        res['angle'] = int(angle)
    return jsonify(res), code


@api_bp.route('/api/servo/status', methods=['GET'])
@api_login_required
def servo_status():
    """Cek status servo saat ini dari ESP8266."""
    res, code = _send_to_esp('/servo/status')
    return jsonify(res), code
