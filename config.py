import os
from dotenv import load_dotenv

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    if not SECRET_KEY:
        print("ПРЕДУПРЕЖДЕНИЕ ИЗ config.py: SECRET_KEY не найден в переменных окружения. Используется небезопасный ключ по умолчанию.")
        SECRET_KEY = 'default-unsafe-secret-key-please-set-in-env'

    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') 
    if not SQLALCHEMY_DATABASE_URI:
        print("ПРЕДУПРЕЖДЕНИЕ ИЗ config.py: SQLALCHEMY_DATABASE_URI не найден в переменных окружения. Используется sqlite:///:memory:")

        db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_path

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or "redis://localhost:6379/0"

    if not SECRET_KEY:
        print("!!! config.py: SECRET_KEY НЕ ЗАГРУЖЕН ИЗ .ENV !!!")
    if not SQLALCHEMY_DATABASE_URI:
        print("!!! config.py: SQLALCHEMY_DATABASE_URI НЕ ЗАГРУЖЕН ИЗ .ENV !!!")