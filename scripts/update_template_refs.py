"""
Script para atualizar referências de templates no app_original.py
"""
import re

# Mapeamento de templates antigos para novos caminhos
template_mapping = {
    'login.html': 'auth/login.html',
    'register.html': 'auth/register.html',
    'dashboard.html': 'user/dashboard.html',
    'profile.html': 'user/profile.html',
    'ranking.html': 'user/ranking.html',
    'chat.html': 'chat/chat.html',
    'faqs.html': 'faq/faqs.html',
    'challenges.html': 'challenges/challenges.html',
    'teams.html': 'teams/teams.html',
    'view_team.html': 'teams/view_team.html',
    'manage_team.html': 'teams/manage_team.html',
    'boss_fights_list_user.html': 'boss_fights/boss_fights_list_user.html',
    'view_boss_fight.html': 'boss_fights/view_boss_fight.html',
    'paths.html': 'learning_paths/paths.html',
    'view_path.html': 'learning_paths/view_path.html',
    'view_battle.html': 'events/view_battle.html',
    'admin_users.html': 'admin/admin_users.html',
    'admin_dashboard.html': 'admin/admin_dashboard.html',
    'admin_teams.html': 'admin/admin_teams.html',
    'admin_faq.html': 'admin/admin_faq.html',
    'admin_levels.html': 'admin/admin_levels.html',
    'admin_challenges.html': 'admin/admin_challenges.html',
    'admin_paths.html': 'admin/admin_paths.html',
    'admin_edit_path.html': 'admin/admin_edit_path.html',
    'admin_achievements.html': 'admin/admin_achievements.html',
    'admin_daily_challenges.html': 'admin/admin_daily_challenges.html',
    'admin_boss_fights.html': 'admin/admin_boss_fights.html',
    'admin_hunts.html': 'admin/admin_hunts.html',
    'admin_edit_hunt.html': 'admin/admin_edit_hunt.html',
    'admin_events.html': 'admin/admin_events.html',
    'admin_edit_event.html': 'admin/admin_edit_event.html',
    'admin_battles.html': 'admin/admin_battles.html',
    'admin_import.html': 'admin/admin_import.html',
}

# Ler o arquivo
with open('app_original.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir cada template
for old_path, new_path in template_mapping.items():
    pattern = f"render_template\\('{old_path}'"
    replacement = f"render_template('{new_path}'"
    content = content.replace(pattern, replacement)

# Salvar o arquivo atualizado
with open('app_original.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Templates atualizados com sucesso!")
print(f"Total de templates mapeados: {len(template_mapping)}")
