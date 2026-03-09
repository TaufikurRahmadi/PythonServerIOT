"""
routes/history.py
====================
Blueprint untuk halaman utama history.
  GET / → tampilkan data sensor terbaru, kontrol servo, tabel riwayat.

Mendukung:
  - Filter tanggal (?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD)
  - Pagination (?page=N)
"""

from flask import Blueprint, request, session, render_template_string
from models.database    import sensor_fetch, sensor_count, sensor_stats, PER_PAGE
from models.decorators  import login_required
from templates.shared_css          import BASE_CSS
from templates.dashboard_template  import DASHBOARD_TEMPLATE
from templates.history_template  import HISTORY_TEMPLATE

# sensor_buffer dan esp_ip diimpor dari api.py (state bersama)
from routes.api import sensor_buffer, esp_ip

history_bp = Blueprint('history', __name__)


def render_history(**kw):
    return render_template_string(HISTORY_TEMPLATE, css=BASE_CSS, **kw)


@history_bp.route('/history')
@login_required
def history():
    # Baca parameter URL
    page      = request.args.get('page', 1, type=int)
    date_from = request.args.get('date_from', '')
    date_to   = request.args.get('date_to',   '')
    offset    = (page - 1) * PER_PAGE

    # Ambil data dari database
    data        = sensor_fetch(PER_PAGE, offset, date_from or None, date_to or None)
    db_total    = sensor_count(date_from or None, date_to or None)
    stats       = sensor_stats(date_from or None, date_to or None)
    total_pages = max(1, (db_total + PER_PAGE - 1) // PER_PAGE)

    # Data terbaru: coba dari buffer memori dulu, lalu dari DB
    latest      = sensor_buffer[-1] if sensor_buffer else (data[0] if data else None)
    servo_angle = latest['servo_angle'] if latest else 0

    return render_history(
        data        = data,
        latest      = latest,
        stats       = stats,
        db_total    = db_total,
        servo_angle = servo_angle,
        esp_ip      = esp_ip,
        username    = session['username'],
        role        = session['role'],
        page        = page,
        total_pages = total_pages,
        date_from   = date_from,
        date_to     = date_to,
    )
