"""
routes/admin.py
===============
Blueprint untuk manajemen user (admin only).

Endpoint:
  GET  /admin/users              → daftar user
  POST /admin/users/add          → tambah user baru
  POST /admin/users/edit         → edit password/role user
  POST /admin/users/delete/<id>  → hapus user (JSON response)
"""

from flask import Blueprint, request, session, redirect, render_template_string, jsonify
from models.database   import (
    get_all_users, get_user_by_id, create_user, get_user_by_username,
    count_admins, hash_password, get_db
)
from models.decorators import admin_required
from templates.shared_css       import BASE_CSS
from templates.users_template   import USERS_TEMPLATE

admin_bp = Blueprint('admin', __name__)


def render_users(**kw):
    return render_template_string(USERS_TEMPLATE, css=BASE_CSS, **kw)


# ── GET /admin/users ─────────────────────────────────────────
@admin_bp.route('/admin/users')
@admin_required
def admin_users():
    # Ambil flash messages yang tersimpan di session
    messages = session.pop('flash_messages', [])
    return render_users(
        users        = get_all_users(),
        username     = session['username'],
        current_user = session['username'],
        messages     = messages,
    )


# ── POST /admin/users/add ────────────────────────────────────
@admin_bp.route('/admin/users/add', methods=['POST'])
@admin_required
def admin_add_user():
    username  = request.form.get('username',  '').strip()
    password  = request.form.get('password',  '')
    password2 = request.form.get('password2', '')
    role      = request.form.get('role', 'viewer')

    def flash_error(msg):
        """Simpan pesan error ke session lalu redirect balik."""
        session.setdefault('flash_messages', []).append((msg, 'error'))
        return redirect('/admin/users')

    # Validasi input
    if len(username) < 3:
        return flash_error('Username minimal 3 karakter.')
    if len(password) < 6:
        return flash_error('Password minimal 6 karakter.')
    if password != password2:
        return flash_error('Konfirmasi password tidak cocok.')
    if get_user_by_username(username):
        return flash_error(f'Username "{username}" sudah digunakan.')

    create_user(username, password, role)
    print(f"[USER] Dibuat: {username} ({role})")
    session.setdefault('flash_messages', []).append(
        (f'User "{username}" berhasil ditambahkan.', 'success')
    )
    return redirect('/admin/users')


# ── POST /admin/users/edit ───────────────────────────────────
@admin_bp.route('/admin/users/edit', methods=['POST'])
@admin_required
def admin_edit_user():
    uid      = request.form.get('user_id', type=int)
    password = request.form.get('password', '').strip()
    role     = request.form.get('role', 'viewer')

    user = get_user_by_id(uid)
    if not user:
        session.setdefault('flash_messages', []).append(('User tidak ditemukan.', 'error'))
        return redirect('/admin/users')

    # Cegah downgrade role jika ini satu-satunya admin
    if user['role'] == 'admin' and role != 'admin':
        if count_admins() <= 1:
            session.setdefault('flash_messages', []).append(
                ('Harus ada minimal 1 admin.', 'warn')
            )
            return redirect('/admin/users')

    # Update data
    with get_db() as conn:
        if password:
            if len(password) < 6:
                session.setdefault('flash_messages', []).append(
                    ('Password minimal 6 karakter.', 'error')
                )
                return redirect('/admin/users')
            conn.execute(
                "UPDATE users SET role=?, password=? WHERE id=?",
                (role, hash_password(password), uid)
            )
        else:
            conn.execute("UPDATE users SET role=? WHERE id=?", (role, uid))
        conn.commit()

    print(f"[USER] Diedit: id={uid} role={role}")
    session.setdefault('flash_messages', []).append(
        (f'User "{user["username"]}" berhasil diperbarui.', 'success')
    )
    return redirect('/admin/users')


# ── POST /admin/users/delete/<id> ────────────────────────────
@admin_bp.route('/admin/users/delete/<int:uid>', methods=['POST'])
@admin_required
def admin_delete_user(uid):
    user = get_user_by_id(uid)
    if not user:
        return jsonify({'status': 'error', 'message': 'User tidak ditemukan'}), 404

    # Tidak bisa hapus akun sendiri
    if user['username'] == session['username']:
        return jsonify({'status': 'error', 'message': 'Tidak bisa menghapus akun sendiri'}), 400

    # Tidak bisa hapus admin terakhir
    if user['role'] == 'admin' and count_admins() <= 1:
        return jsonify({'status': 'error', 'message': 'Harus ada minimal 1 admin'}), 400

    with get_db() as conn:
        conn.execute("DELETE FROM users WHERE id=?", (uid,))
        conn.commit()

    print(f"[USER] Dihapus: {user['username']}")
    return jsonify({'status': 'success'})
