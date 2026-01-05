"""
Utilitários para processamento de arquivos
"""
from PyPDF2 import PdfReader
from flask import flash


def extract_faqs_from_pdf(file_path):
    """
    Extrai FAQs de um arquivo PDF
    
    Args:
        file_path: Caminho para o arquivo PDF
        
    Returns:
        Lista de dicionários com perguntas e respostas
    """
    try:
        faqs = []
        pdf_reader = PdfReader(file_path)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for i in range(0, len(lines) - 1, 2):
            question = lines[i]
            answer = lines[i + 1]
            faqs.append({"question": question, "answer": answer, "image_url": None, "video_url": None})
        return faqs
    except Exception as e:
        flash(f"Erro ao processar o PDF: {str(e)}", 'error')
        return []
