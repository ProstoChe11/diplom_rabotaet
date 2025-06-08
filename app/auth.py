from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user
from app.models import User
from app.forms import LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next') # Добавлено для редиректа
            return redirect(next_page or url_for('routes.dashboard')) # Изменен редирект
        flash('Неверное имя пользователя или пароль')
    return render_template('auth/login.html', form=form) # Убедитесь, что путь к шаблону правильный

@auth_bp.route('/logout')
def logout():
    logout_user()
    # Измените main.index на актуальный home или login, если main.index нет
    return redirect(url_for('routes.login'))