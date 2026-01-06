"""
Agendador de Backups Automáticos
Configura backups periódicos usando APScheduler
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from app.services.backup_service import backup_service
from app.services.notification_service import notification_service


class BackupScheduler:
    """Agendador para backups automáticos"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.app = None
    
    def init_app(self, app):
        """Inicializa o agendador com a aplicação Flask"""
        self.app = app
        
        # Configurar backup diário às 2h da manhã
        self.scheduler.add_job(
            func=self._run_scheduled_backup,
            trigger=CronTrigger(hour=2, minute=0),
            id='daily_backup',
            name='Backup Diário Automático',
            replace_existing=True
        )
        
        # Iniciar scheduler
        if not self.scheduler.running:
            self.scheduler.start()
            print("✓ Agendador de backups iniciado")
    
    def _run_scheduled_backup(self):
        """Executa backup agendado"""
        if not self.app:
            return
        
        with self.app.app_context():
            try:
                # Criar backup
                backup = backup_service.create_backup(
                    created_by=None,
                    backup_type='scheduled',
                    notes=f'Backup automático agendado - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
                )
                
                # Notificar admins
                notification_service.notify_admins(
                    event_type='success',
                    message=f'✓ Backup automático criado com sucesso ({backup.to_dict()["size_mb"]} MB)',
                    category='system'
                )
                
                # Limpar backups antigos (manter últimos 30 backups ou 90 dias)
                removed = backup_service.cleanup_old_backups(keep_count=30, keep_days=90)
                
                if removed > 0:
                    notification_service.notify_admins(
                        event_type='info',
                        message=f'🗑️ {removed} backups antigos foram removidos automaticamente',
                        category='system'
                    )
                
                print(f"✓ Backup automático criado: {backup.filename}")
                
            except Exception as e:
                # Notificar admins sobre erro
                notification_service.notify_admins(
                    event_type='error',
                    message=f'✗ Erro ao criar backup automático: {str(e)}',
                    category='system'
                )
                print(f"✗ Erro no backup automático: {e}")
    
    def shutdown(self):
        """Desliga o agendador"""
        if self.scheduler.running:
            self.scheduler.shutdown()


# Instância global
backup_scheduler = BackupScheduler()
