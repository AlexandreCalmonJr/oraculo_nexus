"""
Modelo de Backup de Banco de Dados
Armazena metadados de backups criados
"""
from datetime import datetime
from app.extensions import db


class DatabaseBackup(db.Model):
    """Modelo para metadados de backups do banco de dados"""
    
    __tablename__ = 'database_backup'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    size_bytes = db.Column(db.BigInteger, nullable=False)
    md5_hash = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    backup_type = db.Column(db.String(20), nullable=False)  # manual, automatic, scheduled
    is_valid = db.Column(db.Boolean, default=True, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    # Relacionamento com User
    creator = db.relationship('User', backref=db.backref('backups_created', lazy='dynamic'))
    
    def to_dict(self):
        """Serializa o backup para JSON"""
        return {
            'id': self.id,
            'filename': self.filename,
            'filepath': self.filepath,
            'size_bytes': self.size_bytes,
            'size_mb': round(self.size_bytes / (1024 * 1024), 2),
            'md5_hash': self.md5_hash,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'creator_name': self.creator.name if self.creator else 'Sistema',
            'backup_type': self.backup_type,
            'is_valid': self.is_valid,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<DatabaseBackup {self.id}: {self.filename}>'
