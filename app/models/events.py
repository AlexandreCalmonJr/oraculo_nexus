"""
Modelos relacionados a eventos (caça ao tesouro e eventos globais)
"""
from datetime import datetime
from app.extensions import db


class ScavengerHunt(db.Model):
    """Caça ao tesouro"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    reward_points = db.Column(db.Integer, default=100)
    steps = db.relationship('ScavengerHuntStep', backref='hunt', lazy='dynamic', order_by='ScavengerHuntStep.step_number', cascade='all, delete-orphan')


class ScavengerHuntStep(db.Model):
    """Passos da caça ao tesouro"""
    id = db.Column(db.Integer, primary_key=True)
    hunt_id = db.Column(db.Integer, db.ForeignKey('scavenger_hunt.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    clue_text = db.Column(db.Text, nullable=False)  # A pista que o bot dá ao utilizador
    target_type = db.Column(db.String(50), nullable=False)  # Ex: 'FAQ', 'CHALLENGE'
    target_identifier = db.Column(db.String(200), nullable=False)  # Ex: O título do desafio
    hidden_clue = db.Column(db.Text, nullable=False)  # A próxima pista a ser revelada


class UserHuntProgress(db.Model):
    """Progresso de usuários na caça ao tesouro"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hunt_id = db.Column(db.Integer, db.ForeignKey('scavenger_hunt.id'), nullable=False)
    current_step = db.Column(db.Integer, default=1, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    user = db.relationship('User', backref='hunt_progress')
    hunt = db.relationship('ScavengerHunt')


class GlobalEvent(db.Model):
    """Eventos globais (World Boss)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    total_hp = db.Column(db.BigInteger, nullable=False)
    current_hp = db.Column(db.BigInteger, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    reward_points_on_win = db.Column(db.Integer, default=200)


class GlobalEventContribution(db.Model):
    """Contribuições de usuários em eventos globais"""
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('global_event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contribution_points = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    event = db.relationship('GlobalEvent', backref=db.backref('contributions', cascade='all, delete-orphan'))
    user = db.relationship('User', backref='event_contributions')
