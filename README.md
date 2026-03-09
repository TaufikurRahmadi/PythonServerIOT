# ESP8266 DHT22 + Servo Dashboard

Dashboard berbasis Flask untuk memantau sensor DHT22 dan mengontrol servo
yang terhubung ke ESP8266. Dilengkapi autentikasi, manajemen user, dan export CSV.

---

## Struktur File

```
esp8266_dashboard/
│
├── app.py                          ← Entry point, inisialisasi Flask & Blueprint
│
├── models/
│   ├── database.py                 ← Semua operasi SQLite (users + sensor_log)
│   └── decorators.py               ← Decorator proteksi route (login, admin)
│
├── routes/
│   ├── auth.py                     ← /login, /logout
│   ├── dashboard.py                ← / (halaman utama)
│   ├── admin.py                    ← /admin/users (manajemen user)
│   └── api.py                      ← /api/... (sensor, servo, export CSV)
│
└── templates/
    ├── shared_css.py               ← CSS global (dark-mode cyberpunk)
    ├── login_template.py           ← HTML halaman login
    ├── dashboard_template.py       ← HTML halaman dashboard
    └── users_template.py           ← HTML halaman manajemen user
```

---

## Tanggung Jawab Tiap File

### `app.py`
Titik masuk aplikasi. Hanya berisi:
- Inisialisasi `Flask` dan `secret_key`
- Pendaftaran semua Blueprint
- Pemanggilan `init_db()` saat pertama jalan

### `models/database.py`
Semua interaksi dengan SQLite:
- `init_db()` — buat tabel & akun admin default
- `create_user / get_user_by_*` — CRUD akun user
- `sensor_insert / sensor_fetch / sensor_count / sensor_stats` — CRUD sensor log
- `hash_password / verify_password` — bcrypt helper

### `models/decorators.py`
Empat decorator untuk proteksi route:

| Decorator            | Digunakan pada    | Jika gagal              |
|----------------------|-------------------|-------------------------|
| `@login_required`    | Halaman HTML      | Redirect ke `/login`    |
| `@admin_required`    | Halaman HTML      | Render halaman 403      |
| `@api_login_required`| Endpoint API      | JSON `401 Unauthorized` |
| `@api_admin_required`| Endpoint API      | JSON `403 Forbidden`    |

### `routes/auth.py`
Login dan logout. Menyimpan `user_id`, `username`, `role` ke session Flask.

### `routes/dashboard.py`
Halaman `/`. Membaca data sensor dari DB (dengan filter & pagination)
dan men-render template dashboard.

### `routes/admin.py`
CRUD user untuk admin:
- Tambah user baru (dengan validasi)
- Edit password dan/atau role
- Hapus user (dengan perlindungan: tidak bisa hapus diri sendiri / admin terakhir)

### `routes/api.py`
Semua endpoint JSON:
- `POST /api/sensor` — menerima data dari ESP8266 (publik, tanpa login)
- `GET /api/sensor` — membaca data (perlu login)
- `GET /api/export/csv` — download CSV (perlu login)
- `POST /api/servo/{open,close,angle}` — kontrol servo (admin only)
- `DELETE /api/sensor/clear` — hapus data (admin only)

### `templates/`
Semua file HTML ditulis sebagai string Python dan di-render dengan
`render_template_string()`. `shared_css.py` berisi CSS global yang
diinjeksi ke setiap template via variabel `{{ css }}`.

---

## Install & Jalankan

```bash
pip install flask requests bcrypt
python app.py
```

Akun default: **admin / admin123** (ganti setelah login pertama!)

---

## Alur Data ESP8266

```
ESP8266
  │  POST /api/sensor  {"temperature":28.5, "humidity":65.2, ...}
  ▼
routes/api.py → receive_sensor()
  │
  ├── Simpan ke sensor_buffer (memori, max 100 item)
  └── Simpan ke tabel sensor_log (SQLite)

Browser
  │  GET /
  ▼
routes/dashboard.py → dashboard()
  │
  ├── Baca sensor_buffer[-1] sebagai data terbaru
  └── Baca sensor_log dari DB untuk tabel riwayat

Browser (Admin)
  │  POST /api/servo/open
  ▼
routes/api.py → servo_open()
  │
  └── GET http://<esp_ip>/servo/open  → ESP8266 gerakkan servo
```
