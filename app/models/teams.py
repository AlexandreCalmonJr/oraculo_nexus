"""
Modelos relacionados a equipes e batalhas entre equipes
"""
from datetime import datetime
from app.extensions import db


class Team(db.Model):
    """Equipes de usuários"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner = db.relationship('User', foreign_keys=[owner_id])
    members = db.relationship('User', foreign_keys='User.team_id', backref='team', lazy='dynamic')
    
    @property
    def total_points(self):
        """Calcula pontos totais da equipe"""
        return sum(member.points for member in self.members)


class TeamBattle(db.Model):
    """Batalhas entre equipes"""
    id = db.Column(db.Integer, primary_key=True)
    challenging_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    challenged_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='active')  # 'active', 'completed', 'expired'
    winner_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)  
    reward_points = db.Column(db.Integer, default=150)
    challenging_team = db.relationship('Team', foreign_keys=[challenging_team_id])
    challenged_team = db.relationship('Team', foreign_keys=[challenged_team_id])
    winner_team = db.relationship('Team', foreign_keys=[winner_team_id])


class TeamBattleChallenge(db.Model):
    """Desafios dentro de uma batalha entre equipes"""
    id = db.Column(db.Integer, primary_key=True)
    battle_id = db.Column(db.Integer, db.ForeignKey('team_battle.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    completed_by_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    battle = db.relationship('TeamBattle', backref=db.backref('battle_challenges', cascade='all, delete-orphan'))
    challenge = db.relationship('Challenge')
