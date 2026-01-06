# Script para adicionar audit logging nas rotas admin
import os
import re

file_path = r'c:\Users\Administrator\oraculo_nexus\app\legacy_routes.py'

# Ler o arquivo
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Adicionar import do audit_service no topo do arquivo
if 'from app.services.audit_service import audit_service' not in content:
    # Encontrar a linha de imports de services
    content = content.replace(
        'from app.services.ai_service import ai_service',
        'from app.services.ai_service import ai_service\nfrom app.services.audit_service import audit_service'
    )
    print("OK: Import do audit_service adicionado")
else:
    print("AVISO: Import do audit_service ja existe")

# 2. Adicionar log na rota de deletar usuario (admin_delete_user)
delete_user_pattern = r"(user_name = user\.name\s+# Remover de equipe se pertencer a alguma)"
delete_user_replacement = r"""user_name = user.name
        
        # Registrar log de auditoria
        audit_service.log_delete(
            admin_id=current_user.id,
            resource_type='User',
            resource_id=user.id,
            resource_name=user_name,
            data={'email': user.email, 'points': user.points}
        )
        
        # Remover de equipe se pertencer a alguma"""

if re.search(delete_user_pattern, content):
    content = re.sub(delete_user_pattern, delete_user_replacement, content)
    print("OK: Audit log adicionado em admin_delete_user")
else:
    print("AVISO: Padrao nao encontrado para admin_delete_user")

# 3. Adicionar log na rota de toggle_admin
toggle_admin_pattern = r"(user\.is_admin = not user\.is_admin\s+db\.session\.commit\(\))"
toggle_admin_replacement = r"""old_status = user.is_admin
        user.is_admin = not user.is_admin
        
        # Registrar log de auditoria
        audit_service.log_update(
            admin_id=current_user.id,
            resource_type='User',
            resource_id=user.id,
            resource_name=user.name,
            old_data={'is_admin': old_status},
            new_data={'is_admin': user.is_admin}
        )
        
        db.session.commit()"""

if re.search(toggle_admin_pattern, content):
    content = re.sub(toggle_admin_pattern, toggle_admin_replacement, content)
    print("OK: Audit log adicionado em toggle_admin")
else:
    print("AVISO: Padrao nao encontrado para toggle_admin")

# 4. Adicionar log na rota de deletar team
delete_team_pattern = r"(db\.session\.delete\(team\)\s+db\.session\.commit\(\)\s+flash\('Time dissolvido com sucesso!', 'success'\))"
delete_team_replacement = r"""# Registrar log de auditoria
        audit_service.log_delete(
            admin_id=current_user.id,
            resource_type='Team',
            resource_id=team.id,
            resource_name=team.name,
            data={'members_count': len(team.members)}
        )
        
        db.session.delete(team)
        db.session.commit()
        flash('Time dissolvido com sucesso!', 'success')"""

if re.search(delete_team_pattern, content):
    content = re.sub(delete_team_pattern, delete_team_replacement, content)
    print("OK: Audit log adicionado em admin_delete_team")
else:
    print("AVISO: Padrao nao encontrado para admin_delete_team")

# Escrever de volta
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nArquivo atualizado com sucesso!")
print("Audit logging integrado em:")
print("- admin_delete_user")
print("- toggle_admin")
print("- admin_delete_team")
