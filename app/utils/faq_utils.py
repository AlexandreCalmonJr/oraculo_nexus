"""
Utilitários para processamento e busca de FAQs
"""
import re
from app.models import FAQ
try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load('pt_core_news_sm')
    except OSError:
        nlp = None
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None


def is_image_url(url):
    """Verifica se a URL é de uma imagem"""
    if not url:
        return False
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp')
    return url.lower().endswith(image_extensions)


def is_video_url(url):
    """Verifica se a URL é de um vídeo"""
    if not url:
        return False
    video_extensions = ('.mp4', '.webm', '.ogg')
    return any(url.lower().endswith(ext) for ext in video_extensions) or 'youtube.com' in url.lower() or 'youtu.be' in url.lower()


def format_faq_response(faq_id, question, answer, image_url=None, video_url=None, file_name=None):
    """
    Formata a resposta de uma FAQ com suporte multimídia
    
    Args:
        faq_id: ID da FAQ
        question: Pergunta
        answer: Resposta
        image_url: URL da imagem (opcional)
        video_url: URL do vídeo (opcional)
        file_name: Nome do arquivo anexo (opcional)
        
    Returns:
        HTML formatado da resposta
    """
    formatted_response = f"<strong>{question}</strong><br><br>"
    has_sections = any(section in answer for section in ["Pré-requisitos:", "Etapa", "Atenção:", "Finalizar:", "Pós-instalação:"])
    
    if has_sections:
        parts = re.split(r'(Pré-requisitos:|Etapa \d+:|Atenção:|Finalizar:|Pós-instalação:)', answer)
        formatted_response += parts[0].replace('\n', '<br>')
        for i in range(1, len(parts), 2):
            header = parts[i]
            content = parts[i+1].replace('\n', '<br>').strip()
            if "Pré-requisitos:" in header:
                formatted_response += f"<strong>✅ {header}</strong><br>{content}<br>"
            elif "Etapa" in header:
                formatted_response += f"<strong>🔧 {header}</strong><br>{content}<br>"
            elif "Atenção:" in header:
                formatted_response += f"<strong>⚠️ {header}</strong><br>{content}<br>"
            elif "Finalizar:" in header:
                formatted_response += f"<strong>⏳ {header}</strong><br>{content}<br>"
            elif "Pós-instalação:" in header:
                formatted_response += f"<strong>✅ {header}</strong><br>{content}<br>"
    else:
        formatted_response += answer.replace('\n', '<br>')

    if image_url and is_image_url(image_url):
        formatted_response += f'<br><img src="{image_url}" alt="Imagem de suporte" style="max-width: 100%; border-radius: 8px; margin-top: 10px;">'
    
    if video_url and is_video_url(video_url):
        if 'youtube.com' in video_url or 'youtu.be' in video_url:
            video_id_match = re.search(r'(?:v=|\/)([a-zA-Z0-9_-]{11})', video_url)
            if video_id_match:
                video_id = video_id_match.group(1)
                formatted_response += f'<div style="position: relative; padding-bottom: 56.25%; margin-top: 10px; height: 0; overflow: hidden; max-width: 100%;"><iframe src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe></div>'
        else:
            formatted_response += f'<br><video controls style="max-width: 100%; border-radius: 8px; margin-top: 10px;"><source src="{video_url}" type="video/mp4">O seu navegador não suporta o vídeo.</video>'
    
    if file_name:
        formatted_response += f'<br><br><a href="/download/{faq_id}" class="text-blue-400 hover:underline" target="_blank">📎 Baixar arquivo: {file_name}</a>'
    
    return formatted_response


def find_faqs_by_keywords(message):
    """
    Busca FAQs por palavras-chave
    
    Args:
        message: Mensagem do usuário
        
    Returns:
        Lista de FAQs ordenadas por relevância
    """
    search_words = set(message.lower().split())
    if not search_words:
        return []
    faqs = FAQ.query.all()
    matches = []
    for faq in faqs:
        question_words = set(faq.question.lower().split())
        answer_words = set(faq.answer.lower().split())
        score = len(search_words.intersection(question_words)) * 2
        score += len(search_words.intersection(answer_words))
        if score > 0:
            matches.append((faq, score))
    matches.sort(key=lambda x: x[1], reverse=True)
    return [match[0] for match in matches]


def find_faq_by_nlp(message):
    """
    Busca FAQs usando NLP (se disponível) ou fallback para keywords
    
    Args:
        message: Mensagem do usuário
        
    Returns:
        Lista de FAQs ordenadas por relevância
    """
    if nlp is None:
        return find_faqs_by_keywords(message)
    
    doc = nlp(message.lower())
    keywords = {token.lemma_ for token in doc if not token.is_stop and not token.is_punct}
    if not keywords:
        return []
    faqs = FAQ.query.all()
    matches = []
    for faq in faqs:
        faq_text = f"{faq.question.lower()} {faq.answer.lower()}"
        faq_doc = nlp(faq_text)
        faq_keywords = {token.lemma_ for token in faq_doc if not token.is_stop and not token.is_punct}
        score = len(keywords.intersection(faq_keywords))
        if score > 0:
            matches.append((faq, score))
    matches.sort(key=lambda x: x[1], reverse=True)
    return [match[0] for match in matches]
