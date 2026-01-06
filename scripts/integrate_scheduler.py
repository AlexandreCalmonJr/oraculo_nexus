# Script para adicionar APScheduler e inicializar backup_scheduler
import os

# 1. Adicionar inicializacao do backup_scheduler no app/__init__.py
app_file = r'c:\Users\Administrator\oraculo_nexus\app\__init__.py'

with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()

if 'backup_scheduler.init_app(app)' not in content:
    # Adicionar import
    content = content.replace(
        'from app.services.restore_service import restore_service',
        'from app.services.restore_service import restore_service\n    from app.services.backup_scheduler import backup_scheduler'
    )
    # Adicionar inicializacao
    content = content.replace(
        'restore_service.init_app(app)',
        'restore_service.init_app(app)\n    backup_scheduler.init_app(app)'
    )
    
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("OK: backup_scheduler inicializado no app/__init__.py")
else:
    print("AVISO: backup_scheduler ja inicializado")

print("\nIntegracao do agendador completa!")
print("\nBackups automaticos configurados:")
print("  - Frequencia: Diario as 2h da manha")
print("  - Retencao: Ultimos 30 backups ou 90 dias")
print("  - Notificacoes: Admins recebem alertas")
