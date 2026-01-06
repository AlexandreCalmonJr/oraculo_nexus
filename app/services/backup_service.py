"""
Serviço de Backup de Banco de Dados
Gerencia criação, validação e listagem de backups
"""
import os
import shutil
import gzip
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from app.extensions import db
from app.models.database_backup import DatabaseBackup


class BackupService:
    """Serviço para gerenciar backups do banco de dados"""
    
    def __init__(self, app=None):
        self.app = app
        self.backup_dir = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o serviço com a aplicação Flask"""
        self.app = app
        self.backup_dir = Path(app.root_path).parent / 'backups' / 'database'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_db_path(self):
        """Retorna o caminho do arquivo de banco de dados"""
        db_uri = self.app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            return Path(db_path)
        return None
    
    def _calculate_md5(self, filepath):
        """Calcula hash MD5 de um arquivo"""
        md5_hash = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    
    def create_backup(self, created_by=None, backup_type='manual', notes=None):
        """
        Cria um novo backup do banco de dados
        
        Args:
            created_by: ID do usuário que criou o backup
            backup_type: Tipo do backup (manual, automatic, scheduled)
            notes: Notas sobre o backup
        
        Returns:
            DatabaseBackup: Objeto do backup criado
        """
        db_path = self._get_db_path()
        if not db_path or not db_path.exists():
            raise FileNotFoundError("Banco de dados não encontrado")
        
        # Gerar nome do arquivo de backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.db.gz'
        backup_filepath = self.backup_dir / backup_filename
        
        # Copiar e comprimir banco de dados
        with open(db_path, 'rb') as f_in:
            with gzip.open(backup_filepath, 'wb', compresslevel=9) as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Calcular hash MD5
        md5_hash = self._calculate_md5(backup_filepath)
        
        # Obter tamanho do arquivo
        size_bytes = backup_filepath.stat().st_size
        
        # Criar registro no banco de dados
        backup = DatabaseBackup(
            filename=backup_filename,
            filepath=str(backup_filepath),
            size_bytes=size_bytes,
            md5_hash=md5_hash,
            created_by=created_by,
            backup_type=backup_type,
            notes=notes
        )
        
        db.session.add(backup)
        db.session.commit()
        
        return backup
    
    def list_backups(self, limit=None, backup_type=None):
        """
        Lista todos os backups disponíveis
        
        Args:
            limit: Número máximo de backups a retornar
            backup_type: Filtrar por tipo de backup
        
        Returns:
            list: Lista de objetos DatabaseBackup
        """
        query = DatabaseBackup.query.order_by(DatabaseBackup.created_at.desc())
        
        if backup_type:
            query = query.filter_by(backup_type=backup_type)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_backup_info(self, backup_id):
        """
        Retorna informações detalhadas de um backup
        
        Args:
            backup_id: ID do backup
        
        Returns:
            DatabaseBackup: Objeto do backup
        """
        return DatabaseBackup.query.get(backup_id)
    
    def validate_backup(self, backup_id):
        """
        Valida a integridade de um backup
        
        Args:
            backup_id: ID do backup
        
        Returns:
            dict: {'is_valid': bool, 'message': str}
        """
        backup = DatabaseBackup.query.get(backup_id)
        if not backup:
            return {'is_valid': False, 'message': 'Backup não encontrado'}
        
        backup_path = Path(backup.filepath)
        if not backup_path.exists():
            backup.is_valid = False
            db.session.commit()
            return {'is_valid': False, 'message': 'Arquivo de backup não encontrado'}
        
        # Verificar hash MD5
        current_md5 = self._calculate_md5(backup_path)
        if current_md5 != backup.md5_hash:
            backup.is_valid = False
            db.session.commit()
            return {'is_valid': False, 'message': 'Hash MD5 não corresponde - arquivo corrompido'}
        
        # Verificar se é um arquivo gzip válido
        try:
            with gzip.open(backup_path, 'rb') as f:
                f.read(1024)  # Ler primeiros bytes para validar
        except Exception as e:
            backup.is_valid = False
            db.session.commit()
            return {'is_valid': False, 'message': f'Arquivo corrompido: {str(e)}'}
        
        backup.is_valid = True
        db.session.commit()
        return {'is_valid': True, 'message': 'Backup válido'}
    
    def delete_backup(self, backup_id):
        """
        Remove um backup
        
        Args:
            backup_id: ID do backup
        
        Returns:
            bool: True se removido com sucesso
        """
        backup = DatabaseBackup.query.get(backup_id)
        if not backup:
            return False
        
        # Remover arquivo físico
        backup_path = Path(backup.filepath)
        if backup_path.exists():
            backup_path.unlink()
        
        # Remover registro do banco
        db.session.delete(backup)
        db.session.commit()
        
        return True
    
    def cleanup_old_backups(self, keep_count=10, keep_days=30):
        """
        Remove backups antigos baseado em política de retenção
        
        Args:
            keep_count: Número de backups recentes a manter
            keep_days: Manter backups dos últimos N dias
        
        Returns:
            int: Número de backups removidos
        """
        cutoff_date = datetime.utcnow() - timedelta(days=keep_days)
        
        # Buscar backups antigos
        old_backups = DatabaseBackup.query.filter(
            DatabaseBackup.created_at < cutoff_date
        ).order_by(DatabaseBackup.created_at.desc()).offset(keep_count).all()
        
        removed_count = 0
        for backup in old_backups:
            if self.delete_backup(backup.id):
                removed_count += 1
        
        return removed_count
    
    def get_backup_stats(self):
        """
        Retorna estatísticas sobre backups
        
        Returns:
            dict: Estatísticas de backups
        """
        total_backups = DatabaseBackup.query.count()
        total_size = db.session.query(
            db.func.sum(DatabaseBackup.size_bytes)
        ).scalar() or 0
        
        latest_backup = DatabaseBackup.query.order_by(
            DatabaseBackup.created_at.desc()
        ).first()
        
        return {
            'total_backups': total_backups,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'latest_backup': latest_backup.to_dict() if latest_backup else None
        }


# Instância global
backup_service = BackupService()
