import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import User, Level
from werkzeug.security import generate_password_hash

def create_admin():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Ensure levels exist
        if Level.query.count() == 0:
            print("Creating levels...")
            from app.config import LEVELS
            for level_name, level_data in LEVELS.items():
                level = Level(name=level_name, min_points=level_data['min_points'], insignia=level_data['insignia'])
                db.session.add(level)
            db.session.commit()

        email = "admin@exemplo.com"
        password = "admin123"
        
        existing_admin = User.query.filter_by(email=email).first()
        if not existing_admin:
            nivel_iniciante = Level.query.filter_by(name='Iniciante').first()
            admin_user = User(
                name="Administrador",
                email=email,
                password=generate_password_hash(password),
                is_admin=True,
                points=0,
                level_id=nivel_iniciante.id if nivel_iniciante else None
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user created: {email} / {password}")
        else:
            print(f"Admin user already exists: {email} / {password}")

if __name__ == "__main__":
    create_admin()
