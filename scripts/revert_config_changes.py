# Script para remover "Config" e reverter CSS do hamburger
import os

# 1. Remover header Config do admin_base.html
admin_file = r'c:\Users\Administrator\oraculo_nexus\templates\admin\admin_base.html'

with open(admin_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Remover o div sidebar-header
old_sidebar = '''        <aside class="sidebar" id="sidebar">
                <div class="sidebar-header">
                        <span class="sidebar-title">Config</span>
                </div>
                <button class="sidebar-toggle"'''

new_sidebar = '''        <aside class="sidebar" id="sidebar">
                <button class="sidebar-toggle"'''

content = content.replace(old_sidebar, new_sidebar)
print("OK: Header 'Config' removido do admin")

with open(admin_file, 'w', encoding='utf-8') as f:
    f.write(content)

# 2. Reverter CSS do sidebar.css para posicionamento original
css_file = r'c:\Users\Administrator\oraculo_nexus\static\sidebar.css'

with open(css_file, 'r', encoding='utf-8') as f:
    css_content = f.read()

# Reverter posicionamento do botao
css_content = css_content.replace(
    '''    position: fixed;
    top: 1rem;
    left: 200px;''',
    '''    position: absolute;
    top: 1rem;
    right: 1rem;'''
)
print("OK: Posicionamento do botao revertido para absolute/right")

# Reverter collapsed
css_content = css_content.replace(
    '''.sidebar.collapsed .sidebar-toggle {
    left: 15px;
    transform: none;
}''',
    '''.sidebar.collapsed .sidebar-toggle {
    right: 50%;
    transform: translateX(50%);
}'''
)
print("OK: Posicionamento colapsado revertido")

# Reverter hover
css_content = css_content.replace(
    '''.sidebar.collapsed .sidebar-toggle:hover {
    transform: scale(1.1);
}''',
    '''.sidebar.collapsed .sidebar-toggle:hover {
    transform: translateX(50%) scale(1.1);
}'''
)
print("OK: Hover colapsado revertido")

# Reverter largura do botao para 40px fixo
css_content = css_content.replace(
    '''    width: auto;
    min-width: 40px;
    padding: 0 0.75rem;''',
    '''    width: 40px;'''
)
print("OK: Largura do botao revertida para 40px")

# Reverter margin-top do sidebar-nav
css_content = css_content.replace(
    'margin-top: 0.5rem;',
    'margin-top: 4.5rem;'
)
print("OK: Margem do sidebar-nav revertida")

# Remover CSS do sidebar-header e toggle-text se existir
if '/* Header do Sidebar */' in css_content:
    # Remover bloco inteiro do header
    start = css_content.find('/* Header do Sidebar */')
    end = css_content.find('/* Botão de Toggle */')
    if start != -1 and end != -1:
        css_content = css_content[:start] + css_content[end:]
        print("OK: CSS do header removido")

if '/* Texto do botao de toggle */' in css_content:
    start = css_content.find('/* Texto do botao de toggle */')
    end = css_content.find('/* ===== TOPBAR (HEADER) ===== */')
    if start != -1 and end != -1:
        css_content = css_content[:start] + css_content[end:]
        print("OK: CSS do toggle-text removido")

with open(css_file, 'w', encoding='utf-8') as f:
    f.write(css_content)

print("\nReversao completa!")
print("Sidebar voltou ao estado original sem 'Config'")
