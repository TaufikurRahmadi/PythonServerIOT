"""
models/decorators.py
====================
Decorator untuk proteksi route:
  - login_required      → redirect ke /login jika belum login
  - admin_required      → tampilkan 403 jika bukan admin (halaman)
  - api_login_required  → return JSON 401 jika belum login (API)
  - api_admin_required  → return JSON 403 jika bukan admin (API)
"""

from functools import wraps
from flask import session, redirect, url_for, request, jsonify, render_template_string
from templates.shared_css import BASE_CSS


# Template sederhana halaman 403
ERROR_403 = f"""<!DOCTYPE html><html><head><style>{BASE_CSS}
body{{display:flex;align-items:center;justify-content:center;padding:20px;}}
.box{{background:var(--panel);border:1px solid rgba(255,23,68,.3);border-radius:14px;
      padding:40px;text-align:center;max-width:400px;}}
h2{{font-size:48px;color:var(--red);margin-bottom:8px;}}
p{{color:var(--muted);margin-bottom:20px;}}
</style></head><body><div class="box">
<h2>403</h2><p>Halaman ini hanya untuk Admin.</p>
<a href="/"><button class="btn btn-cyan">← Kembali</button></a>
</div></body></html>"""


# ── Untuk route halaman (HTML) ───────────────────────────────

def login_required(f):
    """Pastikan user sudah login. Jika belum, redirect ke /login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Pastikan user sudah login DAN memiliki role 'admin'."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login', next=request.path))
        if session.get('role') != 'admin':
            return render_template_string(ERROR_403), 403
        return f(*args, **kwargs)
    return decorated


# ── Untuk endpoint API (JSON response) ──────────────────────

def api_login_required(f):
    """API: kembalikan JSON 401 jika user belum login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


def api_admin_required(f):
    """API: kembalikan JSON 401/403 jika user bukan admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        if session.get('role') != 'admin':
            return jsonify({'status': 'error', 'message': 'Forbidden — admin only'}), 403
        return f(*args, **kwargs)
    return decorated
