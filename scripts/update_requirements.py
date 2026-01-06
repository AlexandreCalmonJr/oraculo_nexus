# Script para atualizar requirements.txt com todas as dependencias
import os

req_file = r'c:\Users\Administrator\oraculo_nexus\requirements.txt'

# Ler requirements atual
with open(req_file, 'r', encoding='utf-8') as f:
    current_reqs = f.read()

# Lista de dependencias necessarias
new_dependencies = [
    'flask-socketio',
    'python-socketio',
    'APScheduler'
]

# Adicionar dependencias que faltam
added = []
for dep in new_dependencies:
    dep_name = dep.split('==')[0].lower()
    if dep_name not in current_reqs.lower():
        current_reqs += f'\n{dep}'
        added.append(dep)
        print(f"OK: Adicionado {dep}")
    else:
        print(f"AVISO: {dep} ja existe")

# Escrever de volta
with open(req_file, 'w', encoding='utf-8') as f:
    f.write(current_reqs)

if added:
    print(f"\n{len(added)} dependencias adicionadas ao requirements.txt")
    print("\nFaca commit e push para o Railway:")
    print("  git add requirements.txt")
    print("  git commit -m 'Add missing dependencies'")
    print("  git push")
else:
    print("\nTodas as dependencias ja estao no requirements.txt")
