"""
templates/login_template.py
============================
Template HTML untuk halaman login.
Di-render menggunakan render_template_string() dari Flask.
"""

LOGIN_TEMPLATE = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Login — ESP8266 Dashboard</title>
  <style>
    {{ css }}

    body { display: flex; align-items: center; justify-content: center; padding: 20px; }

    .wrap { position: relative; z-index: 1; width: 100%; max-width: 400px; }

    .box {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 40px 36px;
      box-shadow: 0 0 60px rgba(0,229,255,.05);
    }
    /* Garis aksen cyan di atas kotak */
    .box::before {
      content: '';
      display: block;
      width: 100%;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--cyan), transparent);
      margin-bottom: 32px;
    }

    .brand { display: flex; align-items: center; gap: 14px; margin-bottom: 28px; }
    .icon  { width: 46px; height: 46px; border-radius: 11px; background: linear-gradient(135deg,#003d4d,#001a24); border: 1px solid var(--cyan); display: flex; align-items: center; justify-content: center; font-size: 22px; box-shadow: 0 0 20px rgba(0,229,255,.15); }
    .brand h2 { font-size: 18px; font-weight: 800; }
    .brand h2 span { color: var(--cyan); }
    .brand p { font-size: 10px; color: var(--muted); letter-spacing: 2px; margin-top: 3px; font-family: 'DM Mono', monospace; }

    .btn-submit {
      width: 100%; padding: 14px;
      background: linear-gradient(135deg, #003d4d, #005566);
      border: 1px solid var(--cyan);
      border-radius: 10px; color: var(--cyan);
      font-family: 'Oxanium', sans-serif; font-size: 14px; font-weight: 700;
      letter-spacing: 2px; cursor: pointer; transition: all .2s; margin-top: 8px;
    }
    .btn-submit:hover { box-shadow: 0 0 30px rgba(0,229,255,.2); transform: translateY(-1px); }

    .note { text-align: center; margin-top: 24px; font-size: 10px; color: var(--muted); font-family: 'DM Mono', monospace; }
  </style>
</head>
<body>
<div class="wrap">
  <div class="box">

    <!-- Branding -->
    <div class="brand">
      <div class="icon">⚙️</div>
      <div>
        <h2>ESP8266 <span>Control</span></h2>
        <p>SECURE DASHBOARD v3.0</p>
      </div>
    </div>

    <!-- Pesan error jika login gagal -->
    {% if error %}
    <div class="alert alert-error">⚠ {{ error }}</div>
    {% endif %}

    <!-- Form login -->
    <form method="POST" action="/login">
      <input type="hidden" name="next" value="{{ next }}"/>
      <div class="field">
        <label>Username</label>
        <input type="text" name="username" autofocus required/>
      </div>
      <div class="field">
        <label>Password</label>
        <input type="password" name="password" required/>
      </div>
      <button type="submit" class="btn-submit">🔐 MASUK</button>
    </form>

    <p class="note">ESP8266 DHT22 + Servo Dashboard</p>
  </div>
</div>
</body>
</html>"""
