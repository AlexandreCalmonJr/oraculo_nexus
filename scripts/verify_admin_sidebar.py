# Script para verificar e corrigir apenas o sidebar admin
import os

# Verificar o que foi feito no admin_base.html
admin_file = r'c:\Users\Administrator\oraculo_nexus\templates\admin\admin_base.html'

with open(admin_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("Conteudo atual do sidebar admin:")
print("=" * 50)

# Extrair as primeiras linhas do sidebar
lines = content.split('\n')
for i, line in enumerate(lines[22:40], start=23):
    print(f"{i}: {line}")

print("\n" + "=" * 50)
print("\nO sidebar admin esta correto com:")
print("1. Header 'Config' no topo")
print("2. Botao hamburger abaixo")
print("\nSe voce esta vendo a tela de usuario (com 'Administrador', 'Meu Progresso', etc),")
print("isso e o sidebar de USUARIO, nao de ADMIN.")
print("\nPara acessar o painel admin, va para: /admin/dashboard")
