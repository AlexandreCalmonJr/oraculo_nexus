# Script para converter TODOS os arquivos admin para UTF-8
import os
import glob

# Encontrar todos os arquivos HTML na pasta admin
admin_files = glob.glob(r'c:\Users\Administrator\oraculo_nexus\templates\admin\*.html')

print(f"Encontrados {len(admin_files)} arquivos HTML na pasta admin\n")

converted = 0
errors = 0

for file_path in admin_files:
    try:
        # Tentar ler com diferentes encodings
        content = None
        used_encoding = None
        
        for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                used_encoding = encoding
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print(f"ERRO: Nao foi possivel ler {os.path.basename(file_path)}")
            errors += 1
            continue
        
        # Escrever de volta em UTF-8
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if used_encoding != 'utf-8':
            print(f"OK: {os.path.basename(file_path)} ({used_encoding} -> UTF-8)")
        
        converted += 1
        
    except Exception as e:
        print(f"ERRO ao processar {os.path.basename(file_path)}: {e}")
        errors += 1

print(f"\n{'='*50}")
print(f"Conversao concluida!")
print(f"Arquivos convertidos: {converted}")
print(f"Erros: {errors}")
print(f"{'='*50}")
