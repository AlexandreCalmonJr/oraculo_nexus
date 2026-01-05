"""
Modelos relacionados a Boss Fights
"""
from datetime import datetime
from app.extensions import db


class BossFight(db.Model):
    """Boss Fight para equipes"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    reward_points = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(255), nullable=True)
    stages = db.relationship('BossFightStage', backref='boss_fight', lazy='dynamic', order_by='BossFightStage.order')


class BossFightStage(db.Model):
    """Etapas de um Boss Fight"""
    id = db.Column(db.Integer, primary_key=True)
    boss_fight_id = db.Column(db.Integer, db.ForeignKey('boss_fight.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    steps = db.relationship('BossFightStep', backref='stage', lazy='dynamic', order_by='BossFightStep.id', cascade='all, delete-orphan')


class BossFightStep(db.Model):
    """Tarefas individuais dentro de uma etapa"""
    id = db.Column(db.Integer, primary_key=True)
    stage_id = db.Column(db.Integer, db.ForeignKey('boss_fight_stage.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    expected_answer = db.Column(db.String(500), nullable=False)


class TeamBossProgress(db.Model):
    """Progresso de uma equipe em um Boss Fight"""
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    step_id = db.Column(db.Integer, db.ForeignKey('boss_fight_step.id'), nullable=False)
    completed_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    team = db.relationship('Team')
    step = db.relationship('BossFightStep')
    user = db.relationship('User')


class TeamBossCompletion(db.Model):
    """Registro de Boss Fights completados por equipes"""
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    boss_fight_id = db.Column(db.Integer, db.ForeignKey('boss_fight.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    team = db.relationship('Team')
    boss_fight = db.relationship('BossFight')
