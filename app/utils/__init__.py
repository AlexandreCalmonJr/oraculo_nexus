"""
Utilitários compartilhados
"""
from app.utils.ticket_utils import process_ticket_command, suggest_solution
from app.utils.faq_utils import (
    find_faq_by_nlp, find_faqs_by_keywords, format_faq_response,
    is_image_url, is_video_url
)
from app.utils.gamification_utils import (
    update_user_level, check_and_award_achievements,
    check_boss_fight_completion, check_and_complete_paths,
    get_or_create_daily_challenge, finalize_ended_battles
)
from app.utils.file_utils import extract_faqs_from_pdf

__all__ = [
    'process_ticket_command', 'suggest_solution',
    'find_faq_by_nlp', 'find_faqs_by_keywords', 'format_faq_response',
    'is_image_url', 'is_video_url',
    'update_user_level', 'check_and_award_achievements',
    'check_boss_fight_completion', 'check_and_complete_paths',
    'get_or_create_daily_challenge', 'finalize_ended_battles',
    'extract_faqs_from_pdf'
]
