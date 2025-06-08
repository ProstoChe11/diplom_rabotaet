from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User
from app.forms import UserForm

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/users')
@login_required
def user_management():
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('main.index')) # Предполагается, что есть main.index, иначе измените
    
    users = User.query.all()
    return render_template('admin/users.html', users=users) # Убедитесь, что путь к шаблону правильный

@admin_bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('main.index')) # Предполагается, что есть main.index, иначе измените
    
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        # Логика обновления пользователя (должна быть в routes.py или здесь)
        user.username = form.username.data
        user.role = form.role.data
        user.full_name = form.full_name.data
        user.contact_info = form.contact_info.data
        if form.password.data:
            user.set_password(form.password.data)
        from app import db # Импорт db, если этот файл отдельный
        db.session.commit()
        flash('Пользователь обновлен')
        return redirect(url_for('admin.user_management'))
    
    return render_template('admin/edit_user.html', form=form, user=user)