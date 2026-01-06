# Script para reposicionar o botao hamburger corretamente
import os

css_file = r'c:\Users\Administrator\oraculo_nexus\static\sidebar.css'

with open(css_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Mudar o posicionamento do botao para nao sobrepor
# Vamos mover ele para a direita e garantir que nao sobreponha
old_position = '''    position: absolute;
    top: 1rem;
    right: 1rem;'''

new_position = '''    position: fixed;
    top: 1rem;
    left: 200px;'''

content = content.replace(old_position, new_position)
print("OK: Posicao do botao alterada para fixed")

# Quando sidebar colapsar, ajustar posicao
old_collapsed = '''.sidebar.collapsed .sidebar-toggle {
    right: 50%;
    transform: translateX(50%);
}'''

new_collapsed = '''.sidebar.collapsed .sidebar-toggle {
    left: 15px;
    transform: none;
}'''

content = content.replace(old_collapsed, new_collapsed)
print("OK: Posicao do botao colapsado ajustada")

# Ajustar hover do colapsado
old_hover = '''.sidebar.collapsed .sidebar-toggle:hover {
    transform: translateX(50%) scale(1.1);
}'''

new_hover = '''.sidebar.collapsed .sidebar-toggle:hover {
    transform: scale(1.1);
}'''

content = content.replace(old_hover, new_hover)
print("OK: Hover do botao colapsado ajustado")

with open(css_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nBotao hamburger reposicionado!")
print("Agora ele fica fora do sidebar e nao sobrepoe os itens")
