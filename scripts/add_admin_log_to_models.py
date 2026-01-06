# Script para adicionar AdminLog ao models/__init__.py
import os

file_path = r'c:\Users\Administrator\oraculo_nexus\app\models\__init__.py'

# Ler o arquivo
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar import do AdminLog
if 'from app.models.admin_log import AdminLog' not in content:
    # Encontrar a linha do Notification
    content = content.replace(
        'from app.models.notifications import Notification',
        'from app.models.notifications import Notification\nfrom app.models.admin_log import AdminLog'
    )
    print("OK: Import do AdminLog adicionado")
else:
    print("AVISO: Import do AdminLog ja existe")

# Adicionar ao __all__
if "'AdminLog'" not in content:
    content = content.replace(
        "'FAQ', 'Notification'",
        "'FAQ', 'Notification', 'AdminLog'"
    )
    print("OK: AdminLog adicionado ao __all__")
else:
    print("AVISO: AdminLog ja esta no __all__")

# Escrever de volta
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Arquivo atualizado!")
