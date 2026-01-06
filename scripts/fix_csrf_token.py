# Script para corrigir csrf_token no template admin_notifications.html
import os

file_path = r'c:\Users\Administrator\oraculo_nexus\templates\admin\admin_notifications.html'

# Ler o arquivo
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir csrf_token() por form.hidden_tag()
old_line = '<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">'
new_line = '{{ form.hidden_tag() }}'

if old_line in content:
    content = content.replace(old_line, new_line)
    print("OK: csrf_token() substituido por form.hidden_tag()")
else:
    print("AVISO: Linha nao encontrada, tentando variacao...")
    # Tentar com espaços diferentes
    old_line2 = '            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">'
    new_line2 = '            {{ form.hidden_tag() }}'
    if old_line2 in content:
        content = content.replace(old_line2, new_line2)
        print("OK: csrf_token() substituido (variacao)")
    else:
        print("ERRO: Nao foi possivel encontrar a linha para substituir")

# Escrever de volta
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Arquivo atualizado!")
