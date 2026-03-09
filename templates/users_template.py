"""
templates/users_template.py
============================
Template HTML untuk halaman manajemen user (admin only).
Fitur: daftar user, tambah user, edit (modal), hapus.

Variabel yang dibutuhkan saat render:
  - css          : BASE_CSS string
  - users        : list of dict (semua user)
  - username     : str nama admin yang sedang login
  - current_user : str username admin (untuk disable tombol hapus diri sendiri)
  - messages     : list of (message, category) untuk flash messages
"""

USERS_TEMPLATE = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Manajemen User — ESP8266</title>
  <style>
    {{ css }}

    body { padding: 0; }
    .page { max-width: 900px; margin: 0 auto; padding: 24px 20px; position: relative; z-index: 1; }

    .page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
    .page-title  { font-size: 20px; font-weight: 800; }
    .page-title span { color: var(--cyan); }

    /* ── Kartu tiap user ── */
    .user-cards { display: grid; gap: 14px; margin-bottom: 28px; }
    .user-card  { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 20px 24px; display: flex; align-items: center; justify-content: space-between; gap: 16px; transition: border-color .3s; }
    .user-card:hover { border-color: rgba(0,229,255,.3); }

    .user-info { display: flex; align-items: center; gap: 16px; }
    .av-big    { width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 700; flex-shrink: 0; }
    .av-big.admin  { background: linear-gradient(135deg,#003d4d,#005566); border: 2px solid var(--cyan);  color: var(--cyan);  }
    .av-big.viewer { background: linear-gradient(135deg,#1a2a1a,#243524); border: 2px solid var(--green); color: var(--green); }

    .u-name    { font-size: 15px; font-weight: 700; margin-bottom: 4px; }
    .u-meta    { font-size: 11px; color: var(--muted); font-family: 'DM Mono', monospace; }
    .u-actions { display: flex; gap: 8px; flex-wrap: wrap; }

    /* ── Form tambah user ── */
    .form-panel { background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 28px; position: relative; overflow: hidden; }
    .form-panel::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg,transparent,var(--cyan),transparent); opacity: .5; }
    .form-title { font-size: 14px; font-weight: 700; letter-spacing: .5px; margin-bottom: 22px; }
    .form-grid  { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

    @media (max-width: 600px) {
      .form-grid  { grid-template-columns: 1fr; }
      .u-actions  { flex-direction: column; }
    }
  </style>
</head>
<body>

<!-- ── Navigasi atas ── -->
<nav class="top-nav">
  <div class="nav-brand">
    <div class="nav-icon">⚙️</div>
    <span class="nav-title">ESP8266 <span>Control</span></span>
  </div>
  <div class="nav-links">
    <a href="/"            class="nav-link">📊 Dashboard</a>
     <a href="/history" class="nav-link"> History</a>
    <a href="/admin/users" class="nav-link active">👥 Users</a>
  </div>
  <div class="nav-right">
    <div class="user-chip">
      <div class="user-av av-admin">{{ username[0].upper() }}</div>
      <span>{{ username }}</span>
      <span class="role-badge role-admin">ADMIN</span>
    </div>
    <a href="/logout"><button class="btn btn-red btn-sm">⏻ Logout</button></a>
  </div>
</nav>

<div class="page">
  <div class="page-header">
    <h2 class="page-title">👥 Manajemen <span>User</span></h2>
    <span style="font-size:11px;color:var(--muted);font-family:'DM Mono',monospace;">{{ users|length }} akun terdaftar</span>
   <button class="btn btn-cyan btn-sm" onclick="openAdd()">
      ➕ Tambah User
    </button>
  </div>

  <!-- Flash messages -->
  {% for msg, cat in messages %}
  <div class="alert alert-{{ cat }}">
    {% if cat=='success' %}✅{% elif cat=='error' %}⚠{% else %}ℹ{% endif %} {{ msg }}
  </div>
  {% endfor %}

  <!-- ── Daftar user ── -->
  <div class="user-cards">
    {% for u in users %}
    <div class="user-card">
      <div class="user-info">
        <div class="av-big {{ u.role }}">{{ u.username[0].upper() }}</div>
        <div>
          <div class="u-name">
            {{ u.username }}
            {% if u.username == current_user %}
              <span style="font-size:10px;color:var(--muted);font-weight:400;">(Anda)</span>
            {% endif %}
          </div>
          <div class="u-meta">
            <span class="role-badge role-{{ u.role }}" style="margin-right:8px;">{{ u.role.upper() }}</span>
            Dibuat: {{ u.created_at[:10] }} &nbsp;·&nbsp;
            Login terakhir: {{ u.last_login[:16] if u.last_login else 'Belum pernah' }}
          </div>
        </div>
      </div>
      <div class="u-actions">
        <button class="btn btn-yellow btn-sm"
                onclick="openEdit({{ u.id }}, '{{ u.username }}', '{{ u.role }}')">✏ Edit</button>

        {% if u.username != current_user %}
          <button class="btn btn-red btn-sm"
                  onclick="deleteUser({{ u.id }}, '{{ u.username }}')">🗑 Hapus</button>
        {% else %}
          <!-- Tidak bisa hapus akun sendiri -->
          <button class="btn btn-sm" style="background:var(--border);border:none;color:var(--muted);cursor:not-allowed;" disabled>🔒 Aktif</button>
        {% endif %}
      </div>
    </div>
    {% endfor %}
  </div>

  <!-- ── Modal tambah user ── -->
<div class="modal-overlay" id="add-modal">
  <div class="modal">
    <button class="modal-close" onclick="closeAdd()">✕</button>
    <h3>➕ Tambah User Baru</h3>

    <form method="POST" action="/admin/users/add">
      <div class="field">
        <label>Username</label>
        <input type="text" name="username" required placeholder="min. 3 karakter"/>
      </div>

      <div class="field">
        <label>Password</label>
        <input type="password" name="password" required placeholder="min. 6 karakter"/>
      </div>

      <div class="field">
        <label>Konfirmasi Password</label>
        <input type="password" name="password2" required placeholder="Ulangi password"/>
      </div>

      <div class="field">
        <label>Role</label>
        <select name="role">
          <option value="viewer">Viewer — hanya lihat data</option>
          <option value="admin">Admin — akses penuh</option>
        </select>
      </div>

      <div style="display:flex;gap:10px;margin-top:12px;">
        <button type="submit" class="btn btn-cyan">➕ Tambah</button>

        <button type="button"
                class="btn btn-sm"
                style="background:var(--border);border:none;color:var(--text);"
                onclick="closeAdd()">
          Batal
        </button>
      </div>
    </form>
  </div>
</div>

 
<!-- ── Modal edit user ── -->
<div class="modal-overlay" id="edit-modal">
  <div class="modal">
    <button class="modal-close" onclick="closeEdit()">✕</button>
    <h3>✏ Edit User: <span id="edit-uname" style="color:var(--cyan)"></span></h3>
    <form method="POST" action="/admin/users/edit" id="edit-form">
      <input type="hidden" name="user_id" id="edit-uid"/>
      <div class="field">
        <label>Password Baru
          <span style="color:var(--muted);font-size:9px;">(kosongkan jika tidak diubah)</span>
        </label>
        <input type="password" name="password" placeholder="min. 6 karakter atau kosongkan"/>
      </div>
      <div class="field">
        <label>Role</label>
        <select name="role" id="edit-role">
          <option value="viewer">Viewer</option>
          <option value="admin">Admin</option>
        </select>
      </div>
      <div style="display:flex;gap:10px;margin-top:8px;">
        <button type="submit" class="btn btn-cyan">💾 Simpan</button>
        <button type="button" class="btn btn-sm"
                style="background:var(--border);border:none;color:var(--text);"
                onclick="closeEdit()">Batal</button>
      </div>
    </form>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
  function showToast(msg, color='#00e5ff') {
    const t = document.getElementById('toast');
    t.style.display = 'block';
    t.style.borderColor = color;
    t.style.color = color;
    t.textContent = msg;
    setTimeout(() => t.style.display = 'none', 2500);
  }

  // ── Buka modal edit dan isi datanya ────────────────
  function openEdit(id, uname, role) {
    document.getElementById('edit-uid').value   = id;
    document.getElementById('edit-uname').textContent = uname;
    document.getElementById('edit-role').value  = role;
    document.querySelector('#edit-form input[name=password]').value = '';
    document.getElementById('edit-modal').classList.add('show');
  }

  function closeEdit() {
    document.getElementById('edit-modal').classList.remove('show');
  }

  // ── Hapus user via fetch (AJAX) ────────────────────
  async function deleteUser(id, uname) {
    if (!confirm(`Hapus user "${uname}"? Tindakan ini tidak bisa dibatalkan.`)) return;
    const res  = await fetch(`/admin/users/delete/${id}`, { method: 'POST' });
    const data = await res.json();
    if (data.status === 'success') {
      showToast('🗑 User dihapus', '#ff1744');
      setTimeout(() => location.reload(), 1200);
    } else {
      showToast('❌ ' + data.message, '#ff6d00');
    }
  }
  function openAdd() {
  document.getElementById('add-modal').classList.add('show');
}

function closeAdd() {
  document.getElementById('add-modal').classList.remove('show');
}

// klik luar modal
document.getElementById('add-modal').addEventListener('click', function(e){
  if (e.target === this) closeAdd();
});

  // Tutup modal jika klik di luar area modal
  document.getElementById('edit-modal').addEventListener('click', function(e) {
    if (e.target === this) closeEdit();
  });
</script>
</body>
</html>"""
