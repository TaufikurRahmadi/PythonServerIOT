"""
routes/auth.py
==============
Blueprint untuk autentikasi:
  GET  /login  → tampilkan form login
  POST /login  → proses login
  GET  /logout → hapus session dan redirect ke /login
"""

from flask import Blueprint, request, session, redirect, render_template_string
from models.database import get_user_by_username, update_last_login, verify_password
from templates.shared_css    import BASE_CSS
from templates.login_template import LOGIN_TEMPLATE

auth_bp = Blueprint('auth', __name__)


def render_login(**kw):
    return render_template_string(LOGIN_TEMPLATE, css=BASE_CSS, **kw)


# ── GET /login → tampilkan halaman login ─────────────────────
# ── POST /login → proses kredensial ─────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Jika sudah login, langsung ke dashboard
    if session.get('user_id'):
        return redirect('/')

    error    = None
    next_url = request.args.get('next', '/')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        next_url = request.form.get('next', '/')

        user = get_user_by_username(username)

        if user and verify_password(password, user['password']):
            # Login berhasil: simpan info ke session
            session['user_id']  = user['id']
            session['username'] = user['username']
            session['role']     = user['role']
            update_last_login(user['id'])
            print(f"[AUTH] Login: {username} ({user['role']})")
            return redirect(next_url or '/')

        # Login gagal
        error = 'Username atau password salah.'
        print(f"[AUTH] Gagal login: {username}")

    return render_login(error=error, next=next_url)


# ── GET /logout → bersihkan session ─────────────────────────
@auth_bp.route('/logout')
def logout():
    print(f"[AUTH] Logout: {session.get('username', '?')}")
    session.clear()
    return redirect('/login')
