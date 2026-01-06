# Script para adicionar DatabaseBackup ao models/__init__.py e registrar blueprint
import os

# 1. Adicionar DatabaseBackup ao models/__init__.py
models_file = r'c:\Users\Administrator\oraculo_nexus\app\models\__init__.py'

with open(models_file, 'r', encoding='utf-8') as f:
    content = f.read()

if 'from app.models.database_backup import DatabaseBackup' not in content:
    content = content.replace(
        'from app.models.admin_log import AdminLog',
        'from app.models.admin_log import AdminLog\nfrom app.models.database_backup import DatabaseBackup'
    )
    content = content.replace(
        "'FAQ', 'Notification', 'AdminLog'",
        "'FAQ', 'Notification', 'AdminLog', 'DatabaseBackup'"
    )
    print("OK: DatabaseBackup adicionado ao models/__init__.py")
else:
    print("AVISO: DatabaseBackup ja existe em models/__init__.py")

with open(models_file, 'w', encoding='utf-8') as f:
    f.write(content)

# 2. Registrar backup blueprint no app/__init__.py
app_file = r'c:\Users\Administrator\oraculo_nexus\app\__init__.py'

with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()

if 'from app.routes.backup import backup_bp' not in content:
    content = content.replace(
        'from app.routes.security import security_bp',
        'from app.routes.security import security_bp\n    from app.routes.backup import backup_bp'
    )
    content = content.replace(
        'app.register_blueprint(security_bp)',
        'app.register_blueprint(security_bp)\n    app.register_blueprint(backup_bp)'
    )
    print("OK: backup_bp registrado no app/__init__.py")
else:
    print("AVISO: backup_bp ja registrado")

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(content)

# 3. Inicializar backup_service no app
if 'backup_service.init_app(app)' not in content:
    # Adicionar import
    content = content.replace(
        'from app.services.notification_service import notification_service',
        'from app.services.notification_service import notification_service\n    from app.services.backup_service import backup_service\n    from app.services.restore_service import restore_service'
    )
    # Adicionar inicializacao
    content = content.replace(
        'notification_service.init_app(app, socketio)',
        'notification_service.init_app(app, socketio)\n    backup_service.init_app(app)\n    restore_service.init_app(app)'
    )
    
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("OK: backup_service e restore_service inicializados")

# 4. Adicionar link no sidebar
sidebar_file = r'c:\Users\Administrator\oraculo_nexus\templates\admin\admin_base.html'

with open(sidebar_file, 'r', encoding='utf-8') as f:
    content = f.read()

if 'backup.backup_page' not in content:
    old_sidebar = '''                        <a href="{{ url_for('security.security_dashboard') }}" class="sidebar-item"><i
                                        class="fas fa-shield-alt"></i><span>Seguranca</span></a>
                        <div class="sidebar-divider"></div>'''
    
    new_sidebar = '''                        <a href="{{ url_for('security.security_dashboard') }}" class="sidebar-item"><i
                                        class="fas fa-shield-alt"></i><span>Seguranca</span></a>
                        <a href="{{ url_for('backup.backup_page') }}" class="sidebar-item"><i
                                        class="fas fa-database"></i><span>Backup de Dados</span></a>
                        <div class="sidebar-divider"></div>'''
    
    content = content.replace(old_sidebar, new_sidebar)
    print("OK: Link de Backup adicionado ao sidebar")
else:
    print("AVISO: Link de Backup ja existe")

with open(sidebar_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nIntegracao completa!")
