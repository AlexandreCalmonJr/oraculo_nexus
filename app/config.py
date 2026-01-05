"""
Configurações da aplicação Service Desk Chat Moderno
"""
import os

class Config:
    """Configurações base da aplicação"""
    
    # Configurações do Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'uma-chave-secreta-padrao-para-desenvolvimento')
    
    # Configurações do Banco de Dados
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///service_desk.db').replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de Upload
    UPLOAD_FOLDER = 'uploads'
    
    # Configurações CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.getenv('CSRF_SECRET_KEY', SECRET_KEY)
    
    # Configurações do Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
    
    # Configurações de Cache
    REDIS_URL = os.getenv('REDIS_URL')
    
    @staticmethod
    def get_cache_config():
        """Retorna configuração de cache baseada na disponibilidade do Redis"""
        redis_url = Config.REDIS_URL
        if redis_url:
            return {'CACHE_TYPE': 'RedisCache', 'CACHE_REDIS_URL': redis_url}
        else:
            return {'CACHE_TYPE': 'SimpleCache'}


# Constantes de Níveis de Gamificação
LEVELS = {
    'Iniciante': {'min_points': 0, 'insignia': '🌱'},
    'Básico': {'min_points': 50, 'insignia': '🌿'},
    'Intermediário': {'min_points': 150, 'insignia': '🌳'},
    'Avançado': {'min_points': 350, 'insignia': '🏆'},
    'Expert': {'min_points': 600, 'insignia': '⭐'},
    'Master': {'min_points': 1000, 'insignia': '👑'}
}
