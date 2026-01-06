# Script para criar as tabelas do banco de dados
import sys
import io

# Configurar encoding para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app, db
from app.models import AdminLog, Notification

app = create_app()

with app.app_context():
    print("Criando tabelas no banco de dados...")
    
    try:
        # Criar todas as tabelas
        db.create_all()
        print("OK: Tabelas criadas com sucesso!")
        
        # Verificar se as tabelas foram criadas
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("\nTabelas no banco de dados:")
        for table in sorted(tables):
            print(f"  - {table}")
        
        # Verificar especificamente as novas tabelas
        if 'admin_log' in tables:
            print("\nOK: Tabela 'admin_log' criada com sucesso!")
        else:
            print("\nERRO: Tabela 'admin_log' nao foi criada")
        
        if 'notification' in tables:
            print("OK: Tabela 'notification' criada com sucesso!")
        else:
            print("ERRO: Tabela 'notification' nao foi criada")
            
    except Exception as e:
        print(f"\nERRO ao criar tabelas: {e}")
        import traceback
        traceback.print_exc()

print("\nProcesso concluido!")
