"""
ESP8266 DHT22 + Servo Dashboard — app.py
========================================
Entry point utama. Hanya berisi inisialisasi Flask dan
pendaftaran semua Blueprint (route).

Jalankan:
    python app.py

Install:
    pip install flask requests bcrypt
"""

import os
from flask import Flask

# ── Import Blueprint dari masing-masing modul route ─────────
from routes.auth    import auth_bp
from routes.dashboard import dashboard_bp
from routes.admin   import admin_bp
from routes.api     import api_bp
from routes.history     import history_bp

# ── Import fungsi inisialisasi DB ────────────────────────────
from models.database import init_db



# ============================================================
# Inisialisasi Aplikasi
# ============================================================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ganti-secret-key-acak-panjang-di-sini!')


# ── Daftarkan semua Blueprint ────────────────────────────────
app.register_blueprint(auth_bp)        # /login, /logout
app.register_blueprint(dashboard_bp)   # /
app.register_blueprint(admin_bp)       # /admin/users, /admin/users/...
app.register_blueprint(api_bp)         # /api/...
app.register_blueprint(history_bp)         # /api/...


# ============================================================
if __name__ == '__main__':
    init_db()

    print("=" * 57)
    print("  ESP8266 Dashboard  [SQLite + Auth + User Mgmt]")
    print("=" * 57)
    print("  Dashboard   : http://0.0.0.0:5000/")
    print("  Login       : http://0.0.0.0:5000/login")
    print("  User Mgmt   : http://0.0.0.0:5000/admin/users")
    print("  Sensor API  : POST http://0.0.0.0:5000/api/sensor")
    print("  Export CSV  : GET  http://0.0.0.0:5000/api/export/csv")
    print("  ── Default account ───────────────────────────")
    print("  User: admin        Pass: admin123  Role: admin")
    print("  (Ganti password setelah login pertama!)")
    print("=" * 57)

    app.run(host='0.0.0.0', port=5000)
  #  app.run(host='0.0.0.0', port=5000, debug=True)
