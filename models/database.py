"""
models/database.py
==================
Semua operasi database: koneksi, inisialisasi tabel,
dan fungsi CRUD untuk tabel `users` dan `sensor_log`.
"""

import sqlite3
import bcrypt
from datetime import datetime

DB_PATH  = 'dashboard.db'
PER_PAGE = 20


# ============================================================
# KONEKSI & INISIALISASI
# ============================================================

def get_db():
    """Buka koneksi SQLite. Row dikembalikan sebagai dict-like object."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # lebih cepat untuk concurrent read/write
    return conn


def init_db():
    """
    Buat tabel jika belum ada, lalu buat akun admin default
    jika belum ada user sama sekali.
    """
    with get_db() as conn:
        # Tabel akun pengguna
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT    NOT NULL UNIQUE,
                password   TEXT    NOT NULL,          -- bcrypt hash
                role       TEXT    NOT NULL DEFAULT 'viewer',
                created_at TEXT    NOT NULL,
                last_login TEXT
            )
        """)
        # Tabel log data sensor
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT    NOT NULL,
                temperature REAL    NOT NULL,
                humidity    REAL    NOT NULL,
                servo_angle INTEGER NOT NULL DEFAULT 0,
                device_id   TEXT,
                ip          TEXT
            )
        """)
        conn.commit()

    # Buat admin default hanya jika tabel users masih kosong
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
        if count == 0:
            create_user('admin', 'admin123', 'admin')
            print("[DB] Akun admin default dibuat: admin / admin123")

    print(f"[DB] Database siap: {DB_PATH}")


# ============================================================
# HELPER PASSWORD (bcrypt)
# ============================================================

def hash_password(password: str) -> str:
    """Hash password menggunakan bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Cocokkan password plain-text dengan hash bcrypt."""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


# ============================================================
# CRUD USERS
# ============================================================

def create_user(username: str, password: str, role: str = 'viewer'):
    """Simpan user baru ke database."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO users (username, password, role, created_at) VALUES (?,?,?,?)",
            (username, hash_password(password), role,
             datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        conn.commit()


def get_user_by_username(username: str):
    """Cari user berdasarkan username. Return dict atau None."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()
    return dict(row) if row else None


def get_user_by_id(uid: int):
    """Cari user berdasarkan ID. Return dict atau None."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id=?", (uid,)
        ).fetchone()
    return dict(row) if row else None


def get_all_users():
    """Ambil semua user (tanpa kolom password). Return list of dict."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, username, role, created_at, last_login "
            "FROM users ORDER BY id"
        ).fetchall()
    return [dict(r) for r in rows]


def update_last_login(uid: int):
    """Catat waktu login terakhir user."""
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET last_login=? WHERE id=?",
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), uid)
        )
        conn.commit()


def count_admins() -> int:
    """Hitung berapa akun dengan role admin (untuk mencegah hapus admin terakhir)."""
    with get_db() as conn:
        return conn.execute(
            "SELECT COUNT(*) as c FROM users WHERE role='admin'"
        ).fetchone()['c']


# ============================================================
# CRUD SENSOR LOG
# ============================================================

def sensor_insert(entry: dict):
    """Simpan satu baris data sensor ke database."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO sensor_log "
            "(timestamp, temperature, humidity, servo_angle, device_id, ip) "
            "VALUES (?,?,?,?,?,?)",
            (entry['timestamp'], entry['temperature'], entry['humidity'],
             entry['servo_angle'], entry['device_id'], entry['ip'])
        )
        conn.commit()


def sensor_fetch(limit=50, offset=0, date_from=None, date_to=None):
    """
    Ambil data sensor dengan pagination dan filter tanggal opsional.
    date_from / date_to format: 'YYYY-MM-DD'
    """
    cond, params = [], []
    if date_from:
        cond.append("timestamp >= ?")
        params.append(date_from + " 00:00:00")
    if date_to:
        cond.append("timestamp <= ?")
        params.append(date_to + " 23:59:59")

    where = ("WHERE " + " AND ".join(cond)) if cond else ""

    with get_db() as conn:
        rows = conn.execute(
            f"SELECT * FROM sensor_log {where} ORDER BY id DESC LIMIT ? OFFSET ?",
            params + [limit, offset]
        ).fetchall()
    return [dict(r) for r in rows]


def sensor_count(date_from=None, date_to=None) -> int:
    """Hitung total baris sensor (dengan filter tanggal opsional)."""
    cond, params = [], []
    if date_from:
        cond.append("timestamp >= ?")
        params.append(date_from + " 00:00:00")
    if date_to:
        cond.append("timestamp <= ?")
        params.append(date_to + " 23:59:59")

    where = ("WHERE " + " AND ".join(cond)) if cond else ""

    with get_db() as conn:
        return conn.execute(
            f"SELECT COUNT(*) as c FROM sensor_log {where}", params
        ).fetchone()['c']


def sensor_stats(date_from=None, date_to=None) -> dict:
    """Hitung min/max suhu dan kelembaban (dengan filter tanggal opsional)."""
    cond, params = [], []
    if date_from:
        cond.append("timestamp >= ?")
        params.append(date_from + " 00:00:00")
    if date_to:
        cond.append("timestamp <= ?")
        params.append(date_to + " 23:59:59")

    where = ("WHERE " + " AND ".join(cond)) if cond else ""

    with get_db() as conn:
        row = conn.execute(
            f"SELECT MIN(temperature) min_temp, MAX(temperature) max_temp, "
            f"MIN(humidity) min_hum, MAX(humidity) max_hum "
            f"FROM sensor_log {where}", params
        ).fetchone()
    return dict(row) if row else {}


def sensor_clear():
    """Hapus semua data sensor dari database."""
    with get_db() as conn:
        conn.execute("DELETE FROM sensor_log")
        conn.commit()
    print("[DB] Semua data sensor dihapus.")
