# Script para adicionar texto "Config" ao botao de toggle do sidebar
import os

sidebar_file = r'c:\Users\Administrator\oraculo_nexus\templates\admin\admin_base.html'

with open(sidebar_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Procurar pela linha do botao sidebar-toggle e adicionar o texto Config
modified = False
for i, line in enumerate(lines):
    if 'class="sidebar-toggle"' in line and i + 1 < len(lines):
        # Verificar se ja tem o texto Config
        if 'toggle-text' not in lines[i+2]:
            # Encontrar a linha com </i> e adicionar o span depois
            for j in range(i, min(i+5, len(lines))):
                if '</i>' in lines[j] and 'toggle-text' not in lines[j]:
                    lines[j] = lines[j].replace('</i>', '</i>\n                        <span class="toggle-text">Config</span>')
                    modified = True
                    print("OK: Texto 'Config' adicionado ao botao de toggle")
                    break
        else:
            print("AVISO: Texto 'Config' ja existe no botao")
        break

if modified:
    with open(sidebar_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

# Adicionar CSS para o texto do toggle
css_file = r'c:\Users\Administrator\oraculo_nexus\static\sidebar.css'

with open(css_file, 'r', encoding='utf-8') as f:
    css_content = f.read()

# Adicionar estilo para toggle-text se nao existir
if '.toggle-text' not in css_content:
    toggle_css = '''
/* Texto do botao de toggle */
.toggle-text {
    margin-left: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
    opacity: 1;
    transition: opacity 0.3s ease;
}

.sidebar.collapsed .toggle-text {
    opacity: 0;
    width: 0;
    margin: 0;
}
'''
    # Adicionar antes do comentario de TOPBAR
    css_content = css_content.replace('/* ===== TOPBAR (HEADER) ===== */', toggle_css + '\n/* ===== TOPBAR (HEADER) ===== */')
    
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("OK: CSS para texto do toggle adicionado")
else:
    print("AVISO: CSS do toggle-text ja existe")

# Ajustar largura do botao de toggle para acomodar o texto
if 'width: 40px;' in css_content and '.sidebar-toggle {' in css_content:
    css_content = css_content.replace(
        '.sidebar-toggle {\n    position: absolute;\n    top: 1rem;\n    right: 1rem;\n    width: 40px;',
        '.sidebar-toggle {\n    position: absolute;\n    top: 1rem;\n    right: 1rem;\n    width: auto;\n    min-width: 40px;\n    padding: 0 0.75rem;'
    )
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("OK: Largura do botao de toggle ajustada")

print("\nAjustes concluidos!")
