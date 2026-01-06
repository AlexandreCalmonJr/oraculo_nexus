# Script para mover texto "Config" para fora do botao hamburger
import os

sidebar_file = r'c:\Users\Administrator\oraculo_nexus\templates\admin\admin_base.html'

with open(sidebar_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Remover o texto Config de dentro do botao
content = content.replace(
    '<span class="toggle-text">Config</span>',
    ''
)
print("OK: Texto Config removido de dentro do botao")

# Adicionar texto Config fora do botao, no topo do sidebar
# Procurar pelo botao sidebar-toggle e adicionar um header antes dele
old_sidebar_start = '''        <aside class="sidebar" id="sidebar">
                <button class="sidebar-toggle"'''

new_sidebar_start = '''        <aside class="sidebar" id="sidebar">
                <div class="sidebar-header">
                        <span class="sidebar-title">Config</span>
                </div>
                <button class="sidebar-toggle"'''

content = content.replace(old_sidebar_start, new_sidebar_start)
print("OK: Header 'Config' adicionado ao topo do sidebar")

with open(sidebar_file, 'w', encoding='utf-8') as f:
    f.write(content)

# Adicionar CSS para o header do sidebar
css_file = r'c:\Users\Administrator\oraculo_nexus\static\sidebar.css'

with open(css_file, 'r', encoding='utf-8') as f:
    css_content = f.read()

# Adicionar estilo para sidebar-header
if '.sidebar-header' not in css_content:
    header_css = '''
/* Header do Sidebar */
.sidebar-header {
    padding: 1rem 1.5rem;
    border-bottom: var(--glass-border);
    margin-bottom: 0.5rem;
}

.sidebar-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    background: linear-gradient(90deg, var(--primary-500), var(--secondary-500));
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    opacity: 1;
    transition: opacity 0.3s ease;
}

.sidebar.collapsed .sidebar-title {
    opacity: 0;
}
'''
    # Adicionar depois do comentario de SIDEBAR
    css_content = css_content.replace(
        '/* Botão de Toggle */',
        header_css + '\n/* Botão de Toggle */'
    )
    
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("OK: CSS do header do sidebar adicionado")

# Ajustar margem do sidebar-nav para acomodar o header
css_content = css_content.replace(
    'margin-top: 4.5rem;',
    'margin-top: 0.5rem;'
)

with open(css_file, 'w', encoding='utf-8') as f:
    f.write(css_content)
print("OK: Margem do sidebar-nav ajustada")

print("\nAjustes concluidos!")
print("Agora 'Config' aparece no topo do sidebar, fora do botao hamburger")
