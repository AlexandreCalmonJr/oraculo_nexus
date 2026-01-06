"""
Serviço de Restauração de Banco de Dados
Gerencia restauração de backups com validação e segurança
"""
import os
import shutil
import gzip
from pathlib import Path
from datetime import datetime
from app.services.backup_service import backup_service


class RestoreService:
    """Serviço para restaurar banco de dados de backups"""
    
    def __init__(self, app=None):
        self.app = app
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o serviço com a aplicação Flask"""
        self.app = app
    
    def _get_db_path(self):
        """Retorna o caminho do arquivo de banco de dados"""
        db_uri = self.app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            return Path(db_path)
        return None
    
    def restore_from_backup(self, backup_id, created_by=None):
        """
        Restaura banco de dados de um backup
        
        Args:
            backup_id: ID do backup a restaurar
            created_by: ID do usuário que está restaurando
        
        Returns:
            dict: {'success': bool, 'message': str, 'safety_backup_id': int}
        """
        from app.models.database_backup import DatabaseBackup
        
        # Buscar backup
        backup = DatabaseBackup.query.get(backup_id)
        if not backup:
            return {'success': False, 'message': 'Backup não encontrado'}
        
        backup_path = Path(backup.filepath)
        if not backup_path.exists():
            return {'success': False, 'message': 'Arquivo de backup não encontrado'}
        
        # Validar backup antes de restaurar
        validation = backup_service.validate_backup(backup_id)
        if not validation['is_valid']:
            return {'success': False, 'message': f'Backup inválido: {validation["message"]}'}
        
        db_path = self._get_db_path()
        if not db_path:
            return {'success': False, 'message': 'Caminho do banco de dados não encontrado'}
        
        try:
            # Criar backup de segurança do banco atual
            safety_backup = backup_service.create_backup(
                created_by=created_by,
                backup_type='automatic',
                notes=f'Backup de segurança antes de restaurar backup #{backup_id}'
            )
            
            # Descomprimir e restaurar
            temp_db_path = db_path.parent / f'temp_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
            
            with gzip.open(backup_path, 'rb') as f_in:
                with open(temp_db_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Substituir banco de dados atual
            if db_path.exists():
                db_path.unlink()
            
            shutil.move(str(temp_db_path), str(db_path))
            
            return {
                'success': True,
                'message': 'Banco de dados restaurado com sucesso',
                'safety_backup_id': safety_backup.id
            }
            
        except Exception as e:
            # Em caso de erro, tentar restaurar o backup de segurança
            if 'safety_backup' in locals():
                try:
                    self.restore_from_backup(safety_backup.id)
                except:
                    pass
            
            return {
                'success': False,
                'message': f'Erro ao restaurar backup: {str(e)}'
            }
    
    def preview_backup(self, backup_id):
        """
        Visualiza informações sobre um backup sem restaurá-lo
        
        Args:
            backup_id: ID do backup
        
        Returns:
            dict: Informações do backup
        """
        from app.models.database_backup import DatabaseBackup
        
        backup = DatabaseBackup.query.get(backup_id)
        if not backup:
            return {'success': False, 'message': 'Backup não encontrado'}
        
        backup_path = Path(backup.filepath)
        if not backup_path.exists():
            return {'success': False, 'message': 'Arquivo de backup não encontrado'}
        
        # Informações básicas
        info = backup.to_dict()
        
        # Verificar tamanho descomprimido (aproximado)
        try:
            with gzip.open(backup_path, 'rb') as f:
                # Ler primeiros bytes para estimar
                sample = f.read(1024 * 1024)  # 1MB
                info['sample_size'] = len(sample)
        except:
            info['sample_size'] = 0
        
        return {'success': True, 'info': info}


# Instância global
restore_service = RestoreService()
