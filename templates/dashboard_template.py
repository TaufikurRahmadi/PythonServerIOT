"""
templates/dashboard_template.py
================================
Template HTML untuk halaman utama dashboard.
Menampilkan: kartu sensor, kontrol servo, statistik, tabel riwayat.

Variabel yang dibutuhkan saat render:
  - css          : BASE_CSS string
  - data         : list of dict (baris tabel)
  - latest       : dict data sensor terbaru (atau None)
  - stats        : dict min/max suhu & kelembaban
  - db_total     : int jumlah total baris
  - servo_angle  : int sudut servo saat ini
  - esp_ip       : str IP ESP8266 (atau None)
  - username     : str nama user yang login
  - role         : str 'admin' atau 'viewer'
  - page         : int halaman saat ini
  - total_pages  : int total halaman
  - date_from    : str filter tanggal mulai
  - date_to      : str filter tanggal akhir
"""

DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard — ESP8266</title>
  <style>
    {{ css }}

    body { padding: 0; }
    .page { max-width: 1140px; margin: 0 auto; padding: 24px 20px; position: relative; z-index: 1; }

    /* ── Kartu sensor suhu & kelembaban ── */
    .sensor-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 20px; }
    .card { background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 26px 28px; position: relative; overflow: hidden; transition: border-color .3s, box-shadow .3s; }
    .card:hover { border-color: var(--cyan); box-shadow: 0 0 30px rgba(0,229,255,.06); }
    .card-glow  { position: absolute; top: -60px; right: -60px; width: 200px; height: 200px; border-radius: 50%; opacity: .06; filter: blur(50px); pointer-events: none; }
    .card.temp  .card-glow { background: var(--orange); }
    .card.humid .card-glow { background: var(--cyan);   }
    .card-label { font-size: 10px; font-weight: 600; letter-spacing: 3px; text-transform: uppercase; color: var(--muted); margin-bottom: 10px; font-family: 'DM Mono', monospace; }
    .card-value { font-size: 60px; font-weight: 800; line-height: 1; letter-spacing: -2px; font-family: 'DM Mono', monospace; }
    .card.temp  .card-value { color: var(--orange); }
    .card.humid .card-value { color: var(--cyan);   }
    .card-unit  { font-size: 22px; font-weight: 300; opacity: .5; }
    .card-sub   { font-size: 11px; color: var(--muted); margin-top: 8px; font-family: 'DM Mono', monospace; }

    /* ── Panel kontrol servo ── */
    .servo-panel { background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 26px 28px; margin-bottom: 20px; position: relative; overflow: hidden; }
    .servo-panel::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, var(--cyan), transparent); opacity: .5; }
    .servo-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 22px; }
    .servo-title  { font-size: 13px; font-weight: 600; letter-spacing: 1px; }
    .servo-state  { font-size: 11px; font-family: 'DM Mono', monospace; padding: 4px 12px; border-radius: 999px; font-weight: 500; }
    .servo-state.on  { background: rgba(0,230,118,.1); color: var(--green); border: 1px solid rgba(0,230,118,.3); }
    .servo-state.off { background: rgba(255,23,68,.1);  color: var(--red);   border: 1px solid rgba(255,23,68,.3);  }

    /* Animasi visual lengan servo */
    .servo-visual { display: flex; align-items: center; gap: 28px; margin-bottom: 22px; }
    .arc-wrap     { position: relative; width: 120px; height: 70px; flex-shrink: 0; }
    .arc-wrap svg { width: 120px; height: 70px; }
    .servo-arm    { position: absolute; bottom: 8px; left: 60px; width: 3px; height: 52px; background: linear-gradient(to top, var(--cyan), rgba(0,229,255,.3)); border-radius: 3px; transform-origin: bottom center; transition: transform .6s cubic-bezier(.34,1.56,.64,1); box-shadow: 0 0 8px rgba(0,229,255,.4); }
    .angle-big    { font-size: 48px; font-weight: 800; color: var(--cyan); font-family: 'DM Mono', monospace; line-height: 1; }
    .angle-lbl    { font-size: 10px; color: var(--muted); letter-spacing: 2px; margin-top: 4px; }

    .servo-btns   { display: flex; gap: 12px; flex-wrap: wrap; }

    /* Slider sudut kustom */
    .slider-wrap { margin-top: 16px; }
    .slider-lbl  { font-size: 10px; color: var(--muted); letter-spacing: 2px; margin-bottom: 8px; }
    input[type=range] { width: 100%; appearance: none; height: 4px; background: var(--border); border-radius: 2px; outline: none; }
    input[type=range]::-webkit-slider-thumb { appearance: none; width: 18px; height: 18px; border-radius: 50%; background: var(--cyan); cursor: pointer; box-shadow: 0 0 10px rgba(0,229,255,.5); }
    .angle-row  { display: flex; align-items: center; gap: 10px; margin-top: 14px; }
    .angle-inp  { background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 10px 14px; border-radius: 8px; font-family: 'DM Mono', monospace; font-size: 14px; width: 100px; outline: none; transition: border-color .2s; }
    .angle-inp:focus { border-color: var(--cyan); }
    .angle-hint { font-size: 11px; color: var(--muted); }

    /* Tampilan terkunci untuk role viewer */
    .servo-locked { opacity: .45; pointer-events: none; }
    .lock-notice  { background: rgba(255,214,0,.06); border: 1px solid rgba(255,214,0,.25); border-radius: 10px; padding: 10px 16px; font-size: 11px; color: var(--yellow); font-family: 'DM Mono', monospace; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }

    /* Info IP ESP8266 */
    .esp-info { background: rgba(0,229,255,.04); border: 1px solid rgba(0,229,255,.15); border-radius: 8px; padding: 10px 16px; font-family: 'DM Mono', monospace; font-size: 11px; color: var(--muted); margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
    .esp-info span { color: var(--cyan); }

    /* Kartu statistik mini */
    .stats-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 20px; }
    .stat-card     { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 16px; font-family: 'DM Mono', monospace; }
    .stat-card .lbl { font-size: 9px; color: var(--muted); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 5px; }
    .stat-card .val { font-size: 15px; font-weight: 500; }

    /* Panel tabel riwayat */
    .tbl-panel { background: var(--panel); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; margin-bottom: 0; }
    .tbl-top   { padding: 16px 22px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
    .tbl-top-title { font-size: 13px; font-weight: 600; }
    .filter-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .filter-inp { background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 7px 12px; border-radius: 8px; font-family: 'DM Mono', monospace; font-size: 12px; outline: none; transition: border-color .2s; }
    .filter-inp:focus { border-color: var(--cyan); }

    /* Badge status suhu */
    .badge        { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 10px; font-weight: 600; }
    .badge-hot    { background: rgba(255,109,0,.15); color: var(--orange); }
    .badge-normal { background: rgba(0,230,118,.1);  color: var(--green);  }
    .badge-cool   { background: rgba(0,229,255,.1);  color: var(--cyan);   }

    .db-badge   { display: inline-flex; align-items: center; gap: 6px; background: rgba(0,229,255,.06); border: 1px solid rgba(0,229,255,.2); border-radius: 6px; padding: 4px 10px; font-size: 10px; font-family: 'DM Mono', monospace; color: var(--muted); }
    .db-badge span { color: var(--cyan); }
    .live-badge { display: flex; align-items: center; gap: 8px; background: rgba(0,230,118,.08); border: 1px solid rgba(0,230,118,.3); border-radius: 999px; padding: 6px 16px; font-size: 11px; font-weight: 600; color: var(--green); letter-spacing: 2px; font-family: 'DM Mono', monospace; }
    .dot  { width: 7px; height: 7px; border-radius: 50%; background: var(--green); animation: blink 1.5s infinite; }
    @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: .2; } }

    @media (max-width: 640px) {
      .sensor-grid { grid-template-columns: 1fr; }
      .live-badge  { display: none; }
    }
  </style>
</head>
<body>

<!-- ── Navigasi atas ──────────────────────────────────── -->
<nav class="top-nav">
  <div class="nav-brand">
    <div class="nav-icon">⚙️</div>
    <span class="nav-title">ESP8266 <span>Control</span></span>
  </div>
  <div class="nav-links">
    <a href="/" class="nav-link active">📊 Dashboard</a>
    <a href="/history" class="nav-link"> History</a>
    {% if role == 'admin' %}
    <a href="/admin/users" class="nav-link">👥 Users</a>
    {% endif %}
  </div>
  <div class="nav-right">
    <div class="live-badge"><div class="dot"></div>ONLINE</div>

    <div class="user-chip">
      <div class="user-av av-{{ role }}">{{ username[0].upper() }}</div>
      <span>{{ username }}</span>
      <span class="role-badge role-{{ role }}">{{ role.upper() }}</span>
    </div>
    <a href="/logout"><button class="btn btn-red btn-sm">⏻ Logout</button></a>
  </div>
</nav>

<div class="page">

  <!-- ── Info IP ESP8266 ── -->
  <div class="esp-info">
    📡 ESP8266:
    <span>{{ esp_ip if esp_ip else 'Belum terdeteksi — tunggu data pertama' }}</span>
  </div>

  <!-- ── Kartu sensor ── -->
  <div class="sensor-grid">
    <div class="card temp">
      <div class="card-glow"></div>
      <div class="card-label">Suhu</div>
      <div class="card-value">
        {% if latest %}{{ "%.1f"|format(latest.temperature) }}{% else %}--{% endif %}
        <span class="card-unit">°C</span>
      </div>
      <div class="card-sub">
        {% if stats and stats.min_temp is not none %}
          Min: {{ "%.1f"|format(stats.min_temp) }}° · Max: {{ "%.1f"|format(stats.max_temp) }}°
        {% else %}Menunggu data...{% endif %}
      </div>
    </div>
    <div class="card humid">
      <div class="card-glow"></div>
      <div class="card-label">Kelembaban</div>
      <div class="card-value">
        {% if latest %}{{ "%.1f"|format(latest.humidity) }}{% else %}--{% endif %}
        <span class="card-unit">%</span>
      </div>
      <div class="card-sub">
        {% if stats and stats.min_hum is not none %}
          Min: {{ "%.1f"|format(stats.min_hum) }}% · Max: {{ "%.1f"|format(stats.max_hum) }}%
        {% else %}Menunggu data...{% endif %}
      </div>
    </div>
  </div>

  <!-- ── Panel kontrol servo ── -->
  <div class="servo-panel">
    <div class="servo-header">
      <span class="servo-title">🔧 KONTROL SERVO</span>
      <span class="servo-state {{ 'on' if servo_angle==180 else 'off' }}" id="servo-badge">
        {{ 'NYALA / TERBUKA' if servo_angle==180 else 'MATI / TERTUTUP' }}
      </span>
    </div>

    <!-- Peringatan jika bukan admin -->


    <div class="">
      <!-- Visual lengan servo -->
      <div class="servo-visual">
        <div class="arc-wrap">
          <svg viewBox="0 0 120 70">
            <path d="M 10 65 A 50 50 0 0 1 110 65" fill="none" stroke="#1a2535" stroke-width="3"/>
            <path d="M 10 65 A 50 50 0 0 1 110 65" fill="none" stroke="#00e5ff" stroke-width="2" stroke-dasharray="157" stroke-dashoffset="157" opacity=".4"/>
            <circle cx="60" cy="65" r="6" fill="#0d1520" stroke="#00e5ff" stroke-width="2"/>
          </svg>
          <div class="servo-arm" id="servo-arm"></div>
        </div>
        <div>
          <div class="angle-big" id="angle-disp">{{ servo_angle }}°</div>
          <div class="angle-lbl">SUDUT SERVO</div>
        </div>
      </div>

      <!-- Tombol cepat -->
      <div class="servo-btns">
        <button class="btn btn-green" onclick="ctrlServo('open')">▶ NYALAKAN (180°)</button>
        <button class="btn btn-red"   onclick="ctrlServo('close')">■ MATIKAN (0°)</button>
      </div>

      <!-- Slider sudut kustom -->
      <div class="slider-wrap">
        <div class="slider-lbl">SUDUT KUSTOM</div>
        <input type="range" min="0" max="180" value="{{ servo_angle }}" id="angle-slider"
               oninput="updateDisp(this.value)" onchange="setAngle(this.value)">
      </div>

      <!-- Input angka manual -->
      <div class="angle-row">
        <input type="number" class="angle-inp" id="angle-inp" min="0" max="180" value="{{ servo_angle }}"/>
        <button class="btn btn-cyan btn-sm" onclick="setFromInput()">SET SUDUT</button>
        <span class="angle-hint">0° — 180°</span>
      </div>
    </div>
  </div>

  <!-- ── Kartu statistik ringkas ── -->
  <div class="stats-row">
    <div class="stat-card"><div class="lbl">Total DB</div><div class="val">{{ db_total }}</div></div>
    <div class="stat-card"><div class="lbl">Device ID</div><div class="val" style="font-size:11px">{{ latest.device_id if latest else 'N/A' }}</div></div>
    <div class="stat-card"><div class="lbl">Update Terakhir</div><div class="val" style="font-size:11px">{{ latest.timestamp if latest else 'N/A' }}</div></div>
    <div class="stat-card"><div class="lbl">Halaman</div><div class="val">{{ page }} / {{ total_pages }}</div></div>
  </div>

  <!-- ── Tabel riwayat sensor ── -->
  <div class="tbl-panel">
    <div class="tbl-top">
      <span class="tbl-top-title">🗄 Riwayat Database</span>

      <!-- Filter tanggal -->
      <form method="GET" action="/" style="display:contents">
        <div class="filter-row">
          <input type="date" name="date_from" class="filter-inp" value="{{ date_from }}" title="Dari"/>
          <input type="date" name="date_to"   class="filter-inp" value="{{ date_to }}"   title="Sampai"/>
          <button type="submit" class="btn btn-cyan btn-sm">🔍 Filter</button>
          <a href="/"><button type="button" class="btn btn-sm" style="background:var(--border);border:none;color:var(--text);">✕</button></a>
        </div>
      </form>

      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <!-- Export CSV -->
        <a href="/api/export/csv{% if date_from or date_to %}?date_from={{ date_from }}&date_to={{ date_to }}{% endif %}"
           class="btn btn-green btn-sm">⬇ CSV</a>
        <!-- Hapus semua (admin only) -->
        {% if role == 'admin' %}
        <button class="btn btn-red btn-sm" onclick="clearDB()">🗑 Hapus Semua</button>
        {% endif %}
      </div>
    </div>

    <!-- Tabel data -->
    <div class="tbl-wrap">
      <table>
        <thead>
          <tr>
            <th>#</th><th>Timestamp</th><th>Suhu °C</th>
            <th>Kelembaban %</th><th>Servo</th><th>Device</th><th>Status</th>
          </tr>
        </thead>
        <tbody>
          {% if data %}
            {% for row in data %}
            <tr>
              <td style="color:var(--muted)">{{ loop.index }}</td>
              <td>{{ row.timestamp }}</td>
              <td style="color:var(--orange);font-weight:600">{{ "%.2f"|format(row.temperature) }}</td>
              <td style="color:var(--cyan);font-weight:600">{{ "%.2f"|format(row.humidity) }}</td>
              <td style="color:var(--muted)">{{ row.servo_angle }}°</td>
              <td style="color:var(--muted);font-size:10px">{{ row.device_id }}</td>
              <td>
                {% if row.temperature >= 35 %}<span class="badge badge-hot">Panas</span>
                {% elif row.temperature <= 20 %}<span class="badge badge-cool">Dingin</span>
                {% else %}<span class="badge badge-normal">Normal</span>{% endif %}
              </td>
            </tr>
            {% endfor %}
          {% else %}
            <tr><td colspan="7" style="text-align:center;padding:40px;color:var(--muted)">Belum ada data...</td></tr>
          {% endif %}
        </tbody>
      </table>
    </div>

   
  </div>

</div><!-- /.page -->

<div class="toast" id="toast"></div>

<script>
  // ── Tampilkan notifikasi toast ──────────────────────
  function showToast(msg, color='#00e5ff') {
    const t = document.getElementById('toast');
    t.style.display = 'block';
    t.style.borderColor = color;
    t.style.color = color;
    t.textContent = msg;
    setTimeout(() => t.style.display = 'none', 2500);
  }

  // ── Update UI servo (visual + badge + input) ────────
  function updateServoUI(angle) {
    document.getElementById('angle-disp').textContent  = angle + '°';
    document.getElementById('angle-slider').value      = angle;
    document.getElementById('angle-inp').value         = angle;
    document.getElementById('servo-arm').style.transform = `rotate(${angle - 90}deg)`;

    const badge = document.getElementById('servo-badge');
    if (angle === 180)      { badge.textContent = 'NYALA / TERBUKA'; badge.className = 'servo-state on';  }
    else if (angle === 0)   { badge.textContent = 'MATI / TERTUTUP'; badge.className = 'servo-state off'; }
    else                    { badge.textContent = angle + '° (KUSTOM)'; badge.className = 'servo-state off'; }
  }

  // Update tampilan saat slider digeser (sebelum release)
  function updateDisp(val) {
    document.getElementById('angle-disp').textContent  = val + '°';
    document.getElementById('angle-inp').value         = val;
    document.getElementById('servo-arm').style.transform = `rotate(${parseInt(val) - 90}deg)`;
  }

  // ── Kirim perintah buka/tutup servo ────────────────
  async function ctrlServo(action) {
    try {
      const res = await fetch(`/api/servo/${action}`, { method: 'POST' });
      if (res.status === 401) { location.href = '/login'; return; }
      const data = await res.json();
      if (data.status === 'success') {
        updateServoUI(action === 'open' ? 180 : 0);
        showToast(
          action === 'open' ? '✅ NYALAKAN → 180°' : '■ MATIKAN → 0°',
          action === 'open' ? '#00e676' : '#ff1744'
        );
      } else {
        showToast('❌ ' + data.message, '#ff6d00');
      }
    } catch(e) { showToast('❌ Gagal', '#ff1744'); }
  }

  // ── Kirim sudut kustom ──────────────────────────────
  async function setAngle(angle) {
    try {
      const res = await fetch(`/api/servo/angle?angle=${angle}`, { method: 'POST' });
      if (res.status === 401) { location.href = '/login'; return; }
      const data = await res.json();
      if (data.status === 'success') {
        updateServoUI(parseInt(angle));
        showToast(`⚙️ Sudut → ${angle}°`);
      }
    } catch(e) { showToast('❌', '#ff1744'); }
  }

  // Baca nilai dari input teks dan kirim
  function setFromInput() {
    const val = parseInt(document.getElementById('angle-inp').value);
    if (isNaN(val) || val < 0 || val > 180) {
      showToast('⚠️ Masukkan angka 0-180', '#ff6d00');
      return;
    }
    setAngle(val);
  }

  // ── Hapus semua data sensor (admin only) ───────────
  async function clearDB() {
    if (!confirm('Hapus SEMUA data sensor? Tidak bisa dibatalkan.')) return;
    const res  = await fetch('/api/sensor/clear', { method: 'DELETE' });
    const data = await res.json();
    if (data.status === 'success') {
      showToast('🗑 DB dikosongkan', '#ff1744');
      setTimeout(() => location.reload(), 1500);
    } else {
      showToast('❌ ' + data.message, '#ff6d00');
    }
  }

  // Set posisi awal servo dari data server
  updateServoUI({{ servo_angle }});

  // Auto-refresh halaman setiap 15 detik
  setTimeout(() => location.reload(), 15000);
</script>
</body>
</html>"""
