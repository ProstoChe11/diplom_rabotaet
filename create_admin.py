from app import create_app
from app.models import User, db

app = create_app()

with app.app_context():
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            role='admin',
            full_name='Главный Администратор',
            contact_info='admin@example.com'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists")