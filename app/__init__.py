"""
Arquivo principal da aplicação Flask
Inicializa a aplicação e registra blueprints
"""
import os
import click
from flask import Flask
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
import cloudinary

from app.config import Config, LEVELS
from app.extensions import db, login_manager, cache
from app.models import User, Level, Category

# Configuração do spaCy
try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load('pt_core_news_sm')
    except OSError:
        print("Modelo pt_core_news_sm não encontrado. Funcionalidades de NLP estarão desabilitadas.")
        nlp = None
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None
    print("spaCy não está disponível. Algumas funcionalidades de NLP estarão desabilitadas.")


def create_app(config_class=Config):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)
    
    # Configurar Cloudinary
    cloudinary.config(
        cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=app.config['CLOUDINARY_API_KEY'],
        api_secret=app.config['CLOUDINARY_API_SECRET'],
        secure=True
    )
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    cache.init_app(app, config=Config.get_cache_config())
    
    # Inicializar SocketIO para notificações em tempo real
    from flask_socketio import SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Inicializar serviço de notificações
    from app.services.notification_service import init_notification_service
    init_notification_service(socketio)
    
    # Registrar event handlers do SocketIO
    from app.socketio_events import register_socketio_events
    register_socketio_events(socketio)
    
    # Armazenar socketio no app para acesso posterior
    app.socketio = socketio
    
    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.notifications import notifications_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(notifications_bp)
    
    # Registrar blueprint da API admin
    from app.routes.admin_api import admin_api_bp
    app.register_blueprint(admin_api_bp)

    
    # Importar rotas do app.py original temporariamente
    # Isso será refatorado gradualmente
    with app.app_context():
        from app import legacy_routes
        legacy_routes.register_routes(app)
    
    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Context processors
    @app.context_processor
    def inject_user_gamification_data():
        from flask_login import current_user
        if current_user.is_authenticated and current_user.level:
            return dict(user_level_insignia=current_user.level.insignia)
        return dict(user_level_insignia='')
    
    @app.context_processor
    def inject_gamification_progress():
        from flask_login import current_user
        if not current_user.is_authenticated:
            return {}
        progress_data = {'percentage': 0, 'next_level_points': None}
        if current_user.level:
            current_level = current_user.level
            next_level = Level.query.filter(Level.min_points > current_level.min_points).order_by(Level.min_points.asc()).first()
            if next_level:
                points_for_level = next_level.min_points - current_level.min_points
                points_achieved = current_user.points - current_level.min_points
                progress_data['percentage'] = max(0, min(100, (points_achieved / points_for_level) * 100 if points_for_level > 0 else 100))
                progress_data['next_level_points'] = next_level.min_points
            else:
                progress_data['percentage'] = 100
        return dict(progress=progress_data)
    
    # Inicializar banco de dados
    with app.app_context():
        initialize_database()
    
    # Comandos CLI
    @app.cli.command(name='create-admin')
    @click.option('--name', required=True, help='O nome do administrador.')
    @click.option('--email', required=True, help='O email do administrador.')
    @click.option('--password', required=True, help='A senha do administrador.')
    def create_admin(name, email, password):
        """Cria um usuário administrador."""
        if User.query.filter_by(email=email).first():
            print(f'Erro: O email {email} já está registrado.')
            return
        initial_level = Level.query.order_by(Level.min_points).first()
        if not initial_level:
            print('Erro: Nenhum nível inicial encontrado. Execute a inicialização do banco de dados primeiro.')
            return
        hashed_password = generate_password_hash(password)
        admin = User(
            name=name,
            email=email,
            password=hashed_password,
            is_admin=True,
            level_id=initial_level.id
        )
        db.session.add(admin)
        db.session.commit()
        print(f'Administrador {name} criado com sucesso!')
    
    return app


def initialize_database():
    """Inicializa o banco de dados com dados padrão"""
    db.create_all()
    
    for level_name, level_data in LEVELS.items():
        if not Level.query.filter_by(name=level_name).first():
            level = Level(name=level_name, min_points=level_data['min_points'], insignia=level_data['insignia'])
            db.session.add(level)
    
    categories = ['Hardware', 'Software', 'Rede', 'Outros', 'Mobile', 'Automation']
    for category_name in categories:
        if not Category.query.filter_by(name=category_name).first():
            category = Category(name=category_name)
            db.session.add(category)
    
    db.session.commit()
