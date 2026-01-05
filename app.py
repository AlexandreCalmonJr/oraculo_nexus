"""
Service Desk Chat Moderno - Aplicação Principal
Versão modularizada mantendo compatibilidade com código existente
"""
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import csv
import json
import re
from PyPDF2 import PdfReader
from datetime import datetime, date, timedelta
try:
    import spacy
    import spacy.cli
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("spaCy não está disponível. Algumas funcionalidades de NLP estarão desabilitadas.")
    
import click
from flask.cli import with_appcontext
from flask_caching import Cache
from sqlalchemy.orm import aliased
import cloudinary
import cloudinary.uploader
import cloudinary.api
from sqlalchemy import func
import random
from flask_wtf import FlaskForm
from wtforms import HiddenField
import uuid
import io

# Importar da estrutura modular
from app.config import Config, LEVELS
from app.extensions import db, login_manager, cache
from app.models import *
from app.utils import *
from app.forms import BaseForm

app = Flask(__name__)

# --- CONFIGURAÇÕES DA APLICAÇÃO ---
app.config.from_object(Config)

# --- CONFIGURAÇÃO DO CLOUDINARY ---
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

# --- INICIALIZAÇÃO DAS EXTENSÕES ---
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
cache.init_app(app, config=Config.get_cache_config())

# Registrar blueprints
from app.routes.auth import auth_bp
from app.routes.user import user_bp

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)

# Configuração do spaCy
nlp = None
if SPACY_AVAILABLE:
    try:
        nlp = spacy.load('pt_core_news_sm')
    except OSError:
        print("Modelo pt_core_news_sm não encontrado. Funcionalidades de NLP estarão desabilitadas.")
        nlp = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def initialize_database():
    """Inicializa o banco de dados com dados padrão"""
    with app.app_context():
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

def generate_invitation_code():
    """Gera um código de convite único."""
    code = str(uuid.uuid4())
    invitation = InvitationCode(code=code)
    db.session.add(invitation)
    db.session.commit()
    return code

# --- CONTEXT PROCESSORS ---
@app.context_processor
def inject_user_gamification_data():
    if current_user.is_authenticated and current_user.level:
        return dict(user_level_insignia=current_user.level.insignia)
    return dict(user_level_insignia='')

@app.context_processor
def inject_gamification_progress():
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

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
with app.app_context():
    initialize_database()

# Importar todas as rotas do arquivo original
# Isso mantém a funcionalidade enquanto gradualmente migramos para blueprints
# IMPORTANTE: Fazer isso DEPOIS de inicializar o banco para evitar conflitos
import sys
sys.path.insert(0, os.path.dirname(__file__))

# Salvar referência ao app antes do import
_app = app

# Importar rotas do app_original
from app_original import *

# Garantir que o app não foi sobrescrito
app = _app

# --- EXECUÇÃO DA APLICAÇÃO ---
if __name__ == '__main__':
    app.run(debug=True)
