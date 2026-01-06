# Script para adicionar link de seguranca no sidebar admin
import os

file_path = r'c:\Users\Administrator\oraculo_nexus\templates\admin\admin_base.html'

# Ler o arquivo
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar link de Dashboard de Seguranca (depois de Logs de Atividade)
if 'security.security_dashboard' not in content:
    old_sidebar = '''                        <a href="{{ url_for('admin_logs.logs_page') }}" class="sidebar-item"><i
                                        class="fas fa-clipboard-list"></i><span>Logs de Atividade</span></a>
                        <div class="sidebar-divider"></div>'''
    
    new_sidebar = '''                        <a href="{{ url_for('admin_logs.logs_page') }}" class="sidebar-item"><i
                                        class="fas fa-clipboard-list"></i><span>Logs de Atividade</span></a>
                        <a href="{{ url_for('security.security_dashboard') }}" class="sidebar-item"><i
                                        class="fas fa-shield-alt"></i><span>Seguranca</span></a>
                        <div class="sidebar-divider"></div>'''
    
    content = content.replace(old_sidebar, new_sidebar)
    print("OK: Link de Dashboard de Seguranca adicionado ao sidebar")
else:
    print("AVISO: Link de Dashboard de Seguranca ja existe")

# Escrever de volta
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Arquivo atualizado com sucesso!")
