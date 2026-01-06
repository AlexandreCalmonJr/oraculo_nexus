# Script para corrigir o JavaScript do formulário de broadcast
import os

file_path = r'c:\Users\Administrator\oraculo_nexus\templates\admin\admin_notifications.html'

# Ler o arquivo
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Encontrar e substituir a linha do CSRF token no JavaScript
old_code = "                    'X-CSRFToken': formData.get('csrf_token')"
new_code = "                    'X-CSRFToken': e.target.querySelector('input[name=\"csrf_token\"]').value"

if old_code in content:
    content = content.replace(old_code, new_code)
    print("OK: Codigo JavaScript corrigido para extrair CSRF token corretamente")
else:
    print("AVISO: Codigo nao encontrado exatamente, tentando buscar...")
    # Mostrar o que está no arquivo
    if "'X-CSRFToken'" in content:
        print("Encontrado 'X-CSRFToken' no arquivo")
    else:
        print("ERRO: Nao encontrado 'X-CSRFToken'")

# Escrever de volta
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Arquivo atualizado!")
