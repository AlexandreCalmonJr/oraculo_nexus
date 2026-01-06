# Script para ajustar sidebar e botoes de backup
import os

# 1. Mudar avatar de "Admin" para "A"
sidebar_file = r'c:\Users\Administrator\oraculo_nexus\templates\admin\admin_base.html'

with open(sidebar_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Trocar "Admin" por "A" no avatar
content = content.replace(
    '<div class="sidebar-user-avatar">Admin</div>',
    '<div class="sidebar-user-avatar">A</div>'
)
print("OK: Avatar alterado de 'Admin' para 'A'")

# 2. Adicionar nome "Config" no item vazio do sidebar
# Procurar por item sem texto e adicionar "Config"
if '<span></span>' in content or 'sidebar-item"><i' in content:
    # Adicionar Config onde estiver vazio
    content = content.replace(
        'class="sidebar-item"><i\n                                        class="fas fa-cog"></i><span></span></a>',
        'class="sidebar-item"><i\n                                        class="fas fa-cog"></i><span>Config</span></a>'
    )
    print("OK: Nome 'Config' adicionado ao item do sidebar")

with open(sidebar_file, 'w', encoding='utf-8') as f:
    f.write(content)

# 3. Ajustar botoes no template de backup
backup_template = r'c:\Users\Administrator\oraculo_nexus\templates\admin\admin_backup.html'

with open(backup_template, 'r', encoding='utf-8') as f:
    content = f.read()

# Melhorar estilo dos botoes de acao
old_action_btn = '''    .action-btn {
        padding: 0.375rem 0.75rem;
        background: var(--bg-tertiary);
        border: none;
        border-radius: 0.375rem;
        color: var(--text-primary);
        cursor: pointer;
        font-size: 0.875rem;
        margin: 0 0.25rem;
        transition: all 0.2s ease;
    }

    .action-btn:hover {
        background: var(--bg-quaternary);
    }'''

new_action_btn = '''    .action-btn {
        padding: 0.5rem 0.75rem;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        color: var(--text-primary);
        cursor: pointer;
        font-size: 0.875rem;
        margin: 0 0.25rem;
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
    }

    .action-btn:hover {
        background: var(--bg-quaternary);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .action-btn i {
        font-size: 1rem;
    }'''

content = content.replace(old_action_btn, new_action_btn)
print("OK: Estilo dos botoes de acao melhorado")

with open(backup_template, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nAjustes concluidos com sucesso!")
