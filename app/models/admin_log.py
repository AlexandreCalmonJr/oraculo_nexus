"""
Modelo de Log de Atividades Administrativas
Rastreia todas as ações executadas por administradores
"""
from datetime import datetime
from app.extensions import db


class AdminLog(db.Model):
    """Modelo para logs de auditoria de ações administrativas"""
    
    __tablename__ = 'admin_log'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # CREATE, UPDATE, DELETE, VIEW, EXPORT, etc.
    resource_type = db.Column(db.String(50), nullable=False)  # User, Challenge, Team, etc.
    resource_id = db.Column(db.Integer, nullable=True)  # ID do recurso afetado
    description = db.Column(db.Text, nullable=False)  # Descrição detalhada
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 ou IPv6
    user_agent = db.Column(db.String(255), nullable=True)  # Browser/client info
    changes = db.Column(db.JSON, nullable=True)  # Detalhes das mudanças (antes/depois)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamento com User
    admin = db.relationship('User', backref=db.backref('admin_logs', lazy='dynamic'))
    
    def to_dict(self):
        """Serializa o log para JSON"""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'admin_name': self.admin.name if self.admin else 'Unknown',
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'description': self.description,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'changes': self.changes or {},
            'created_at': self.created_at.isoformat(),
            'timestamp': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<AdminLog {self.id}: {self.admin.name if self.admin else "Unknown"} - {self.action} {self.resource_type}>'
    
    @staticmethod
    def get_action_icon(action):
        """Retorna ícone FontAwesome para cada tipo de ação"""
        icons = {
            'CREATE': 'fa-plus-circle',
            'UPDATE': 'fa-edit',
            'DELETE': 'fa-trash',
            'VIEW': 'fa-eye',
            'EXPORT': 'fa-download',
            'LOGIN': 'fa-sign-in-alt',
            'LOGOUT': 'fa-sign-out-alt',
            'BROADCAST': 'fa-broadcast-tower',
            'IMPORT': 'fa-upload'
        }
        return icons.get(action, 'fa-info-circle')
    
    @staticmethod
    def get_action_color(action):
        """Retorna cor para cada tipo de ação"""
        colors = {
            'CREATE': 'success',
            'UPDATE': 'info',
            'DELETE': 'danger',
            'VIEW': 'secondary',
            'EXPORT': 'warning',
            'LOGIN': 'primary',
            'LOGOUT': 'secondary',
            'BROADCAST': 'info',
            'IMPORT': 'warning'
        }
        return colors.get(action, 'secondary')
