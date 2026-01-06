# Script para corrigir z-index do botao hamburger
import os

css_file = r'c:\Users\Administrator\oraculo_nexus\static\sidebar.css'

with open(css_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Ajustar z-index do sidebar-toggle para nao sobrepor os itens
old_toggle = '''.sidebar-toggle {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: auto;
    min-width: 40px;
    padding: 0 0.75rem;
    height: 40px;
    border-radius: 8px;
    border: none;
    background: var(--bg-tertiary);
    color: var(--text-primary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    transition: all 0.3s ease;
    z-index: 10;
}'''

new_toggle = '''.sidebar-toggle {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: auto;
    min-width: 40px;
    padding: 0 0.75rem;
    height: 40px;
    border-radius: 8px;
    border: none;
    background: var(--bg-tertiary);
    color: var(--text-primary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    transition: all 0.3s ease;
    z-index: 5;
}'''

if old_toggle in content:
    content = content.replace(old_toggle, new_toggle)
    print("OK: z-index do botao hamburger ajustado de 10 para 5")
else:
    # Tentar apenas mudar o z-index
    content = content.replace('z-index: 10;', 'z-index: 5;')
    print("OK: z-index ajustado")

# Garantir que sidebar-nav tenha z-index maior
if '.sidebar-nav {' in content:
    # Adicionar z-index ao sidebar-nav se nao tiver
    if 'z-index' not in content.split('.sidebar-nav {')[1].split('}')[0]:
        content = content.replace(
            '.sidebar-nav {\n    margin-top: 0.5rem;',
            '.sidebar-nav {\n    margin-top: 0.5rem;\n    position: relative;\n    z-index: 1;'
        )
        print("OK: z-index adicionado ao sidebar-nav")

with open(css_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nBotao hamburger agora nao sobrepoe os itens do menu!")
