"""
Modelos relacionados a desafios
"""
from datetime import datetime, date
from app.extensions import db


class Challenge(db.Model):
    """Desafios para os usuários completarem"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    expected_answer = db.Column(db.String(500), nullable=False)
    points_reward = db.Column(db.Integer, default=10)
    level_required = db.Column(db.String(50), default='Iniciante')
    is_team_challenge = db.Column(db.Boolean, default=False)
    hint = db.Column(db.Text, nullable=True)
    hint_cost = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    challenge_type = db.Column(db.String(50), nullable=False, default='text')
    expected_output = db.Column(db.Text, nullable=True)


class UserChallenge(db.Model):
    """Registro de desafios completados por usuários"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='completed_challenges')
    challenge = db.relationship('Challenge')


class DailyChallenge(db.Model):
    """Desafio diário com pontos bônus"""
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date, unique=True, nullable=False, default=date.today)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    bonus_points = db.Column(db.Integer, default=20)
    challenge = db.relationship('Challenge')
