"""
templates/shared_css.py
========================
CSS global yang dipakai bersama oleh semua halaman.
Ditulis sebagai string Python agar bisa di-inject langsung
ke dalam template HTML (render_template_string).

Desain: dark-mode cyberpunk dengan aksen cyan/orange/green.
"""

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Oxanium:wght@300;400;600;800&family=DM+Mono:wght@300;400;500&display=swap');

/* ── Variabel warna global ─────────────────────────── */
:root {
  --bg:     #070b10;   /* latar belakang utama */
  --panel:  #0d1520;   /* kartu / panel */
  --border: #1a2535;   /* garis batas */
  --cyan:   #00e5ff;
  --orange: #ff6d00;
  --green:  #00e676;
  --red:    #ff1744;
  --yellow: #ffd600;
  --text:   #cfd8e3;
  --muted:  #4a5f75;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Oxanium', sans-serif;
  min-height: 100vh;
}
/* Efek scanline tipis di seluruh layar */
body::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background: repeating-linear-gradient(
    0deg, transparent, transparent 2px,
    rgba(0,229,255,0.015) 2px, rgba(0,229,255,0.015) 4px
  );
}
a { color: inherit; text-decoration: none; }

/* ── Alert / notifikasi ─────────────────────────────── */
.alert {
  padding: 12px 18px; border-radius: 10px;
  font-size: 13px; font-family: 'DM Mono', monospace;
  margin-bottom: 20px; display: flex; align-items: center; gap: 10px;
}
.alert-success { background: rgba(0,230,118,.1);  border: 1px solid rgba(0,230,118,.3);  color: var(--green);  }
.alert-error   { background: rgba(255,23,68,.1);   border: 1px solid rgba(255,23,68,.3);   color: var(--red);    }
.alert-warn    { background: rgba(255,214,0,.1);   border: 1px solid rgba(255,214,0,.3);   color: var(--yellow); }

/* ── Tombol (btn) ───────────────────────────────────── */
.btn {
  padding: 10px 22px; border-radius: 9px; border: none;
  font-family: 'Oxanium', sans-serif; font-size: 13px; font-weight: 600;
  cursor: pointer; letter-spacing: 1px; transition: all .2s;
  display: inline-flex; align-items: center; gap: 7px;
}
.btn-cyan   { background: linear-gradient(135deg,#002233,#003344); border: 1px solid var(--cyan);   color: var(--cyan);   }
.btn-green  { background: linear-gradient(135deg,#003d1a,#005724); border: 1px solid var(--green);  color: var(--green);  }
.btn-red    { background: linear-gradient(135deg,#3d0010,#57001a); border: 1px solid var(--red);    color: var(--red);    }
.btn-yellow { background: linear-gradient(135deg,#332900,#4d3d00); border: 1px solid var(--yellow); color: var(--yellow); }
.btn-cyan:hover   { box-shadow: 0 0 24px rgba(0,229,255,.25);  transform: translateY(-1px); }
.btn-green:hover  { box-shadow: 0 0 24px rgba(0,230,118,.25);  transform: translateY(-1px); }
.btn-red:hover    { box-shadow: 0 0 24px rgba(255,23,68,.25);  transform: translateY(-1px); }
.btn-yellow:hover { box-shadow: 0 0 24px rgba(255,214,0,.2);   transform: translateY(-1px); }
.btn-sm { padding: 6px 14px; font-size: 11px; }

/* ── Input form ─────────────────────────────────────── */
.field { margin-bottom: 18px; }
.field label {
  display: block; font-size: 10px; color: var(--muted);
  letter-spacing: 2px; text-transform: uppercase;
  font-family: 'DM Mono', monospace; margin-bottom: 8px;
}
.field input, .field select {
  width: 100%; background: var(--bg); border: 1px solid var(--border);
  border-radius: 10px; color: var(--text); padding: 12px 16px;
  font-family: 'DM Mono', monospace; font-size: 14px; outline: none;
  transition: border-color .2s, box-shadow .2s;
}
.field input:focus, .field select:focus {
  border-color: var(--cyan);
  box-shadow: 0 0 0 3px rgba(0,229,255,.08);
}
.field select option { background: var(--panel); }

/* ── Navigasi atas ──────────────────────────────────── */
.top-nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 28px; border-bottom: 1px solid var(--border);
  position: relative; z-index: 1;
}
.nav-brand   { display: flex; align-items: center; gap: 12px; }
.nav-icon    { width: 38px; height: 38px; border-radius: 9px; background: linear-gradient(135deg,#003d4d,#001a24); border: 1px solid var(--cyan); display: flex; align-items: center; justify-content: center; font-size: 18px; }
.nav-title   { font-size: 17px; font-weight: 800; letter-spacing: 1px; }
.nav-title span { color: var(--cyan); }
.nav-links   { display: flex; align-items: center; gap: 6px; }
.nav-link    { padding: 7px 14px; border-radius: 8px; font-size: 12px; font-weight: 600; letter-spacing: .5px; transition: all .2s; color: var(--muted); }
.nav-link:hover  { background: rgba(255,255,255,.04); color: var(--text); }
.nav-link.active { background: rgba(0,229,255,.08); color: var(--cyan); border: 1px solid rgba(0,229,255,.2); }
.nav-right   { display: flex; align-items: center; gap: 10px; }
.user-chip   { display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,.03); border: 1px solid var(--border); border-radius: 999px; padding: 5px 12px 5px 8px; font-size: 11px; font-family: 'DM Mono', monospace; }
.user-av     { width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; }
.av-admin    { background: linear-gradient(135deg,#003d4d,#005566); border: 1px solid var(--cyan);  color: var(--cyan);  }
.av-viewer   { background: linear-gradient(135deg,#1a2a1a,#243524); border: 1px solid var(--green); color: var(--green); }
.role-badge  { font-size: 9px; letter-spacing: 1.5px; padding: 2px 8px; border-radius: 999px; }
.role-admin  { background: rgba(0,229,255,.1);  color: var(--cyan);  border: 1px solid rgba(0,229,255,.25);  }
.role-viewer { background: rgba(0,230,118,.1);  color: var(--green); border: 1px solid rgba(0,230,118,.25); }

/* ── Tabel ──────────────────────────────────────────── */
.tbl-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
thead th { padding: 11px 20px; text-align: left; font-size: 9px; color: var(--muted); text-transform: uppercase; letter-spacing: 2px; font-weight: 500; background: rgba(255,255,255,.015); font-family: 'DM Mono', monospace; white-space: nowrap; }
tbody tr { border-top: 1px solid var(--border); }
tbody tr:hover { background: rgba(255,255,255,.015); }
tbody td { padding: 12px 20px; font-size: 12px; font-family: 'DM Mono', monospace; }

/* ── Pagination ─────────────────────────────────────── */
.pager { display: flex; align-items: center; gap: 8px; padding: 14px 22px; border-top: 1px solid var(--border); justify-content: center; flex-wrap: wrap; }
.pg-btn { background: var(--border); border: none; color: var(--text); width: 32px; height: 32px; border-radius: 6px; cursor: pointer; font-size: 12px; font-family: 'DM Mono', monospace; transition: background .2s; }
.pg-btn:hover  { background: #253549; }
.pg-btn.active { background: var(--cyan); color: var(--bg); font-weight: 700; }
.pg-info { font-size: 11px; color: var(--muted); font-family: 'DM Mono', monospace; }

/* ── Toast (notifikasi pojok kanan bawah) ───────────── */
.toast {
  position: fixed; bottom: 24px; right: 24px; z-index: 9999;
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 10px; padding: 14px 20px; font-size: 13px;
  display: none; box-shadow: 0 8px 32px rgba(0,0,0,.5);
  animation: toastIn .3s ease;
}
@keyframes toastIn { from { transform: translateX(20px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

/* ── Modal dialog ───────────────────────────────────── */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.7); z-index: 100; display: none; align-items: center; justify-content: center; }
.modal-overlay.show { display: flex; }
.modal { background: var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 32px; width: 100%; max-width: 440px; position: relative; }
.modal::before { content: ''; display: block; width: 100%; height: 2px; background: linear-gradient(90deg,transparent,var(--cyan),transparent); margin-bottom: 24px; }
.modal h3 { font-size: 16px; font-weight: 800; margin-bottom: 20px; }
.modal-close { position: absolute; top: 16px; right: 16px; background: none; border: none; color: var(--muted); font-size: 20px; cursor: pointer; }
.modal-close:hover { color: var(--text); }

/* ── Responsif mobile ───────────────────────────────── */
@media (max-width: 700px) {
  .nav-links { display: none; }
  .stats-row { grid-template-columns: 1fr 1fr !important; }
}
/* ───────────────── RESPONSIVE LAYOUT ───────────────── */

/* Tablet */
@media (max-width: 1024px) {

  .top-nav{
    flex-wrap:wrap;
    gap:10px;
  }

  .nav-right{
    width:100%;
    justify-content:flex-end;
  }

  table{
    font-size:11px;
  }

  tbody td{
    padding:10px 14px;
  }

  thead th{
    padding:10px 14px;
  }

}


/* Mobile besar */
@media (max-width: 768px) {

  body{
    font-size:14px;
  }

  .top-nav{
    flex-direction:column;
    align-items:flex-start;
    gap:12px;
    padding:16px;
  }

  .nav-right{
    width:100%;
    justify-content:space-between;
  }

  .nav-links{
    display:flex;
    width:100%;
    overflow-x:auto;
    padding-bottom:6px;
  }

  .nav-link{
    white-space:nowrap;
  }

  .modal{
    padding:22px;
    margin:10px;
  }

  .btn{
    padding:10px 16px;
    font-size:12px;
  }

  .btn-sm{
    padding:6px 10px;
  }

}


/* Mobile kecil */
@media (max-width: 480px) {

  .nav-title{
    font-size:14px;
  }

  .nav-icon{
    width:32px;
    height:32px;
    font-size:14px;
  }

  .user-chip{
    font-size:10px;
  }

  .field input,
  .field select{
    padding:10px 12px;
    font-size:13px;
  }

  .modal{
    width:95%;
    padding:18px;
  }

  table{
    font-size:10px;
  }

  tbody td{
    padding:8px 10px;
  }

  thead th{
    font-size:8px;
  }

  .pager{
    gap:6px;
  }

  .pg-btn{
    width:28px;
    height:28px;
  }

}
"""
