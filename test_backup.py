# Script para criar tabela database_backup e testar backup
import sys
import io

# Configurar encoding para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app, db
from app.models import DatabaseBackup
from app.services.backup_service import backup_service

app = create_app()

with app.app_context():
    print("Criando tabela database_backup...")
    
    try:
        # Criar tabela
        db.create_all()
        print("OK: Tabela database_backup criada!")
        
        # Testar criacao de backup
        print("\nTestando criacao de backup...")
        backup = backup_service.create_backup(
            created_by=None,
            backup_type='automatic',
            notes='Backup inicial de teste'
        )
        
        print(f"OK: Backup criado com sucesso!")
        print(f"  - ID: {backup.id}")
        print(f"  - Arquivo: {backup.filename}")
        print(f"  - Tamanho: {backup.to_dict()['size_mb']} MB")
        print(f"  - Hash MD5: {backup.md5_hash}")
        
        # Validar backup
        print("\nValidando backup...")
        validation = backup_service.validate_backup(backup.id)
        if validation['is_valid']:
            print("OK: Backup validado com sucesso!")
        else:
            print(f"ERRO: {validation['message']}")
        
        # Estatisticas
        print("\nEstatisticas de backup:")
        stats = backup_service.get_backup_stats()
        print(f"  - Total de backups: {stats['total_backups']}")
        print(f"  - Espaco total: {stats['total_size_mb']} MB")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()

print("\nProcesso concluido!")
