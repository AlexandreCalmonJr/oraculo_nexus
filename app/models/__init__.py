"""
Importa todos os modelos para facilitar o acesso
"""
from app.models.user import User, InvitationCode
from app.models.gamification import Level, Achievement, UserAchievement
from app.models.content import Category, FAQ
from app.models.challenges import Challenge, UserChallenge, DailyChallenge
from app.models.teams import Team, TeamBattle, TeamBattleChallenge
from app.models.boss_fights import (
    BossFight, BossFightStage, BossFightStep, 
    TeamBossProgress, TeamBossCompletion
)
from app.models.learning_paths import LearningPath, PathChallenge, UserPathProgress
from app.models.events import (
    ScavengerHunt, ScavengerHuntStep, UserHuntProgress,
    GlobalEvent, GlobalEventContribution
)
from app.models.chat import ChatMessage, Ticket
from app.models.notifications import Notification

__all__ = [
    'User', 'InvitationCode',
    'Level', 'Achievement', 'UserAchievement',
    'Category', 'FAQ',
    'Challenge', 'UserChallenge', 'DailyChallenge',
    'Team', 'TeamBattle', 'TeamBattleChallenge',
    'BossFight', 'BossFightStage', 'BossFightStep', 'TeamBossProgress', 'TeamBossCompletion',
    'LearningPath', 'PathChallenge', 'UserPathProgress',
    'ScavengerHunt', 'ScavengerHuntStep', 'UserHuntProgress',
    'GlobalEvent', 'GlobalEventContribution',
    'ChatMessage', 'Ticket',
    'Notification'
]
