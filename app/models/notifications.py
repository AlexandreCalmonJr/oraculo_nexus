"""
Modelo de Notificações
Armazena notificações persistentes para os usuários
"""
from datetime import datetime
from app.extensions import db


class Notification(db.Model):
    """Modelo de notificação persistente"""
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Null para notificações globais
    type = db.Column(db.String(20), nullable=False)  # success, info, warning, error
    category = db.Column(db.String(50), nullable=False)  # achievement, challenge, level_up, team, boss, system, etc.
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.JSON, nullable=True)  # Dados adicionais em formato JSON
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamento com usuário
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic', cascade='all, delete-orphan'))
    
    def to_dict(self):
        """Converte notificação para dicionário"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'category': self.category,
            'message': self.message,
            'data': self.data or {},
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'timestamp': self.created_at.isoformat()  # Para compatibilidade com frontend
        }
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.category} - {self.type}>'
