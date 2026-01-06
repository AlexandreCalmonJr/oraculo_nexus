# Script para adicionar audit logging em rotas de criação/edição
import os
import re

file_path = r'c:\Users\Administrator\oraculo_nexus\app\legacy_routes.py'

# Ler o arquivo
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

changes_made = []

# 1. Adicionar log na criação de FAQ
create_faq_pattern = r"(db\.session\.add\(new_faq\)\s+db\.session\.commit\(\)\s+flash\('FAQ criada com sucesso!', 'success'\))"
create_faq_replacement = r"""db.session.add(new_faq)
                db.session.commit()
                
                # Registrar log de auditoria
                audit_service.log_create(
                    admin_id=current_user.id,
                    resource_type='FAQ',
                    resource_id=new_faq.id,
                    resource_name=question[:50]
                )
                
                flash('FAQ criada com sucesso!', 'success')"""

if re.search(create_faq_pattern, content):
    content = re.sub(create_faq_pattern, create_faq_replacement, content)
    changes_made.append("create_faq")

# 2. Adicionar log na criação de Level
create_level_pattern = r"(db\.session\.add\(level\)\s+db\.session\.commit\(\)\s+flash\('Nível criado com sucesso!', 'success'\))"
create_level_replacement = r"""db.session.add(level)
                db.session.commit()
                
                # Registrar log de auditoria
                audit_service.log_create(
                    admin_id=current_user.id,
                    resource_type='Level',
                    resource_id=level.id,
                    resource_name=name
                )
                
                flash('Nível criado com sucesso!', 'success')"""

if re.search(create_level_pattern, content):
    content = re.sub(create_level_pattern, create_level_replacement, content)
    changes_made.append("create_level")

# 3. Adicionar log na exclusão de Level
delete_level_pattern = r"(level = Level\.query\.get_or_404\(level_id\)\s+db\.session\.delete\(level\)\s+db\.session\.commit\(\))"
delete_level_replacement = r"""level = Level.query.get_or_404(level_id)
        
        # Registrar log de auditoria
        audit_service.log_delete(
            admin_id=current_user.id,
            resource_type='Level',
            resource_id=level.id,
            resource_name=level.name,
            data={'min_points': level.min_points}
        )
        
        db.session.delete(level)
        db.session.commit()"""

if re.search(delete_level_pattern, content):
    content = re.sub(delete_level_pattern, delete_level_replacement, content)
    changes_made.append("delete_level")

# 4. Adicionar log na exclusão de FAQ
delete_faq_pattern = r"(faq = FAQ\.query\.get_or_404\(faq_id\)\s+db\.session\.delete\(faq\)\s+db\.session\.commit\(\)\s+flash\('FAQ excluída com sucesso!', 'success'\))"
delete_faq_replacement = r"""faq = FAQ.query.get_or_404(faq_id)
        
        # Registrar log de auditoria
        audit_service.log_delete(
            admin_id=current_user.id,
            resource_type='FAQ',
            resource_id=faq.id,
            resource_name=faq.question[:50]
        )
        
        db.session.delete(faq)
        db.session.commit()
        flash('FAQ excluída com sucesso!', 'success')"""

if re.search(delete_faq_pattern, content):
    content = re.sub(delete_faq_pattern, delete_faq_replacement, content)
    changes_made.append("delete_faq")

# 5. Adicionar log na exportação de FAQs
export_faq_pattern = r"(faqs = FAQ\.query\.all\(\)\s+faqs_data = \[\])"
export_faq_replacement = r"""faqs = FAQ.query.all()
        
        # Registrar log de auditoria
        audit_service.log_export(
            admin_id=current_user.id,
            resource_type='FAQ',
            count=len(faqs),
            format='JSON'
        )
        
        faqs_data = []"""

if re.search(export_faq_pattern, content):
    content = re.sub(export_faq_pattern, export_faq_replacement, content)
    changes_made.append("export_faqs")

# Escrever de volta
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nArquivo atualizado com sucesso!")
print(f"Audit logging integrado em {len(changes_made)} rotas:")
for change in changes_made:
    print(f"- {change}")

if len(changes_made) == 0:
    print("AVISO: Nenhuma mudanca foi aplicada. Os padroes podem ja ter sido modificados.")
