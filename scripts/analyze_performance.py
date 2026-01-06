# Script de Otimizacao de Performance
# Identifica e corrige problemas comuns de lentidao

import os

print("=== ANALISE DE PERFORMANCE ===\n")

# 1. Verificar se spaCy esta sendo carregado (pode ser lento)
init_file = r'c:\Users\Administrator\oraculo_nexus\app\__init__.py'
with open(init_file, 'r', encoding='utf-8') as f:
    content = f.read()

if 'spacy.load' in content:
    print("PROBLEMA 1: spaCy sendo carregado no startup")
    print("  - Isso pode adicionar 2-5 segundos no carregamento")
    print("  - Solucao: Carregar sob demanda (lazy loading)")
    print()

# 2. Verificar queries sem paginacao
routes_dir = r'c:\Users\Administrator\oraculo_nexus\app\routes'
slow_queries = []

for filename in os.listdir(routes_dir):
    if filename.endswith('.py'):
        filepath = os.path.join(routes_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                if '.query.all()' in line and 'paginate' not in ''.join(lines[max(0,i-5):i+5]):
                    slow_queries.append(f"{filename}:{i}")

if slow_queries:
    print(f"PROBLEMA 2: {len(slow_queries)} queries sem paginacao encontradas")
    print("  - Queries .all() podem ser lentas com muitos registros")
    for q in slow_queries[:5]:
        print(f"    - {q}")
    print()

# 3. Verificar se cache esta configurado
if 'cache.init_app' in content:
    print("OK: Cache configurado")
else:
    print("PROBLEMA 3: Cache nao esta sendo usado")
    print("  - Adicionar cache pode melhorar muito a performance")
    print()

# 4. Verificar eager loading
print("\nRECOMENDACOES DE OTIMIZACAO:\n")
print("1. Lazy loading do spaCy")
print("2. Adicionar paginacao em queries grandes")
print("3. Usar cache para dados estaticos")
print("4. Adicionar indices no banco de dados")
print("5. Usar eager loading para relacionamentos")
print("6. Minificar CSS/JS")
print("7. Usar CDN para bibliotecas")
print("\nExecute os scripts de otimizacao para aplicar as melhorias.")
