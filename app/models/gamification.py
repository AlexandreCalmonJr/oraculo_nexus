"""
Modelos relacionados a gamificação (níveis e conquistas)
"""
from datetime import datetime
from app.extensions import db


class Level(db.Model):
    """Níveis de progressão do usuário"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    min_points = db.Column(db.Integer, unique=True, nullable=False, index=True)
    insignia = db.Column(db.String(255), nullable=True)  # URL ou emoji


class Achievement(db.Model):
    """Conquistas desbloqueáveis"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(255), nullable=True)
    trigger_type = db.Column(db.String(50), nullable=False)
    trigger_value = db.Column(db.Integer, nullable=False)


class UserAchievement(db.Model):
    """Conquistas desbloqueadas por usuários"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='achievements')
    achievement = db.relationship('Achievement')
