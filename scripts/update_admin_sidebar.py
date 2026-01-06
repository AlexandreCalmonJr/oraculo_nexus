# Script para adicionar Admin Logs ao sidebar e mudar nome do usuario
import os

file_path = r'c:\Users\Administrator\oraculo_nexus\templates\admin\admin_base.html'

# Ler o arquivo
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Adicionar link de Admin Logs no sidebar (depois de Notificacoes)
if 'admin_logs.logs_page' not in content:
    old_sidebar = '''                        <a href="{{ url_for('notifications.admin_notifications') }}" class="sidebar-item"><i
                                        class="fas fa-bell"></i><span>Notificações</span></a>
                        <div class="sidebar-divider"></div>'''
    
    new_sidebar = '''                        <a href="{{ url_for('notifications.admin_notifications') }}" class="sidebar-item"><i
                                        class="fas fa-bell"></i><span>Notificações</span></a>
                        <a href="{{ url_for('admin_logs.logs_page') }}" class="sidebar-item"><i
                                        class="fas fa-clipboard-list"></i><span>Logs de Atividade</span></a>
                        <div class="sidebar-divider"></div>'''
    
    content = content.replace(old_sidebar, new_sidebar)
    print("OK: Link de Admin Logs adicionado ao sidebar")
else:
    print("AVISO: Link de Admin Logs ja existe")

# 2. Mudar nome do usuario de "A" para "Admin"
content = content.replace(
    '<div class="sidebar-user-avatar">A</div>',
    '<div class="sidebar-user-avatar">Admin</div>'
)
print("OK: Avatar alterado para 'Admin'")

# Escrever de volta
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Arquivo atualizado com sucesso!")
