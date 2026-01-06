"""
Modelos relacionados a trilhas de aprendizagem
"""
from datetime import datetime
from app.extensions import db


class PathChallenge(db.Model):
    """Associação entre trilhas e desafios"""
    path_id = db.Column(db.Integer, db.ForeignKey('learning_path.id'), primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), primary_key=True)
    step = db.Column(db.Integer, nullable=False)
    challenge = db.relationship('Challenge')
    path = db.relationship('LearningPath', back_populates='challenges')


class LearningPath(db.Model):
    """Trilhas de aprendizagem"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    reward_points = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)
    challenges = db.relationship('PathChallenge', order_by='PathChallenge.step', cascade='all, delete-orphan', back_populates='path')


class UserPathProgress(db.Model):
    """Progresso de usuários em trilhas de aprendizagem"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    path_id = db.Column(db.Integer, db.ForeignKey('learning_path.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    user = db.relationship('User')
    path = db.relationship('LearningPath')
