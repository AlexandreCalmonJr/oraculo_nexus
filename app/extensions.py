"""
Extensões Flask compartilhadas
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache

# Inicializar extensões
db = SQLAlchemy()
login_manager = LoginManager()
cache = Cache()
