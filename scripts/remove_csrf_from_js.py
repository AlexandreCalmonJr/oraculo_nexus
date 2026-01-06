# Script para remover a linha do CSRF token do JavaScript
import os

file_path = r'c:\Users\Administrator\oraculo_nexus\templates\admin\admin_notifications.html'

# Ler o arquivo
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remover a linha do X-CSRFToken do JavaScript
old_code = """                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': e.target.querySelector('input[name="csrf_token"]').value
                },"""

new_code = """                headers: {
                    'Content-Type': 'application/json'
                },"""

if old_code in content:
    content = content.replace(old_code, new_code)
    print("OK: Linha do CSRF token removida do JavaScript")
else:
    print("AVISO: Codigo nao encontrado exatamente")

# Escrever de volta
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Arquivo atualizado!")
