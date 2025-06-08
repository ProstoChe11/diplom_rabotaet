# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from flask_caching import Cache
from celery import Celery

load_dotenv() 

db = SQLAlchemy()
login_manager = LoginManager()
#migrate = Migrate()
cache = Cache()
celery = Celery(__name__)

def create_app(config_object_name='config.Config', config_overrides=None): 
    print(f"ЗАПУСК create_app. CWD: {os.getcwd()}")
    app = Flask(__name__, instance_relative_config=True) 
    print(f"ОБЪЕКТ APP СОЗДАН. app.root_path: {app.root_path}") 
    print(f"app.instance_path: {app.instance_path}")

    try:
        app.config.from_object(config_object_name)
        app.logger.info(f"Успешно загружена конфигурация из: {config_object_name}")

        if not app.config.get('SECRET_KEY'):
             app.logger.warning(f"{config_object_name} загружен, но SECRET_KEY в нем отсутствует или None.")
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
             app.logger.warning(f"{config_object_name} загружен, но SQLALCHEMY_DATABASE_URI в нем отсутствует или None.")

    except ImportError:
        app.logger.error(
            f"Не удалось импортировать объект конфигурации '{config_object_name}'. "
            "Проверьте, что файл существует и путь указан верно. "
            "Попытка загрузить из переменных окружения напрямую."
        )
        
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() in ('true', '1', 't')
        app.config['CELERY_BROKER_URL'] = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
        app.config['CELERY_RESULT_BACKEND'] = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    
    if config_overrides:
        app.config.update(config_overrides)
        app.logger.info("Применены переопределения конфигурации.")

    
    if not app.config.get('SECRET_KEY'):
        app.logger.critical("КРИТИЧЕСКАЯ ОШИБКА: SECRET_KEY не установлен! Установите его в .env или config.py.")
        
        app.config['SECRET_KEY'] = 'unsafe-default-key-change-me-immediately'

    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.logger.warning(
            "ПРЕДУПРЕЖДЕНИЕ: SQLALCHEMY_DATABASE_URI не установлен. "
            "Будет использована база данных SQLite в памяти (данные не сохранятся). "
            "Установите его в .env или config.py."
        )
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 

    
    if app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS') is None:
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    
    if app.config.get('TESTING'):
        app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:')
        app.config.setdefault('WTF_CSRF_ENABLED', False)
        app.config.setdefault('SERVER_NAME', 'localhost.test') 
        app.config.setdefault('CACHE_TYPE', 'NullCache')
        app.config.setdefault('CELERY_TASK_ALWAYS_EAGER', True)
        app.config.setdefault('CELERY_BROKER_URL', 'memory://')
        app.config.setdefault('CELERY_RESULT_BACKEND', 'rpc://')
        app.logger.info("Применена конфигурация для режима ТЕСТИРОВАНИЯ.")

    
    secret_key_display = app.config.get('SECRET_KEY', 'НЕ УСТАНОВЛЕН')
    if secret_key_display != 'НЕ УСТАНОВЛЕН' and len(secret_key_display) > 4:
        secret_key_display = '*' * (len(secret_key_display) - 4) + secret_key_display[-4:]
    app.logger.info(f"Финальный SECRET_KEY: {secret_key_display}")
    app.logger.info(f"Финальный SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    app.logger.info(f"Финальный SQLALCHEMY_TRACK_MODIFICATIONS: {app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS')}")


    db.init_app(app)
    migrate = Migrate()
    login_manager.init_app(app)
    migrate.init_app(app, db) 

    login_manager.login_view = 'routes.login'
    login_manager.login_message = "Пожалуйста, войдите в систему для доступа к этой странице."
    login_manager.login_message_category = "info"

    current_cache_config = {key: app.config[key] for key in app.config if key.startswith('CACHE_')}
    if not current_cache_config.get('CACHE_TYPE'):
        current_cache_config['CACHE_TYPE'] = app.config.get('CACHE_TYPE', 'SimpleCache') 
    cache.init_app(app, config=current_cache_config)
    app.logger.info(f"Кэш сконфигурирован с типом: {current_cache_config.get('CACHE_TYPE')}")

    celery_broker_url = app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    celery_result_backend = app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    celery.conf.broker_url = celery_broker_url
    celery.conf.result_backend = celery_result_backend
    celery.conf.update(app.config) 
    app.logger.info(f"Celery сконфигурирован с брокером: {celery_broker_url}")


    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app

def init_default_data(current_app):
    """Инициализирует данные по умолчанию: админа."""
    from app.models import User 

    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            role='admin',
            full_name='Администратор'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        current_app.logger.info("Добавление пользователя admin по умолчанию.")
        try:
            db.session.commit()
            current_app.logger.info("Пользователь admin по умолчанию успешно создан.")
        except Exception as e:
            current_app.logger.error(f"Ошибка при создании пользователя admin по умолчанию: {e}")
            db.session.rollback()
    else:
        current_app.logger.info("Пользователь admin по умолчанию уже существует.")