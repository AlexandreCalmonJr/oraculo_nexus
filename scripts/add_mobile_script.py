# Script para adicionar sidebar_mobile.js nos templates

import os

templates = [
    r'c:\Users\Administrator\oraculo_nexus\templates\admin\admin_base.html',
    r'c:\Users\Administrator\oraculo_nexus\templates\user\base_user.html'
]

script_tag = '<script src="{{ url_for(\'static\', filename=\'sidebar_mobile.js\') }}"></script>'

for template_path in templates:
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se ja existe
    if 'sidebar_mobile.js' in content:
        print(f"AVISO: sidebar_mobile.js ja existe em {os.path.basename(template_path)}")
        continue
    
    # Adicionar antes do </body>
    if '</body>' in content:
        content = content.replace('</body>', f'    {script_tag}\n</body>')
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"OK: Script adicionado em {os.path.basename(template_path)}")
    else:
        print(f"ERRO: Tag </body> nao encontrada em {os.path.basename(template_path)}")

print("\nSidebar mobile configurado!")
print("\nFuncionalidades:")
print("- Botao hamburger fixo no canto superior esquerdo")
print("- Sidebar desliza da esquerda ao clicar")
print("- Overlay escuro ao abrir")
print("- Fecha ao clicar fora ou em qualquer link")
print("- Largura maior (280px) para melhor usabilidade")
