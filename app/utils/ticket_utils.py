"""
Utilitários para processamento de tickets
"""
import re
from app.models import Ticket
from app.extensions import db


def process_ticket_command(message):
    """
    Processa comandos relacionados a tickets
    
    Args:
        message: Mensagem do usuário
        
    Returns:
        Resposta do comando ou None se não for um comando de ticket
    """
    match = re.match(r"Encerrar chamado (\d+)", message)
    if match:
        ticket_id = match.group(1)
        ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
        if ticket:
            if ticket.status == 'Aberto':
                ticket.status = 'Fechado'
                db.session.commit()
                return f"Chamado {ticket_id} encerrado com sucesso."
            else:
                return f"Chamado {ticket_id} já está fechado."
        return f"Chamado {ticket_id} não encontrado."
    return None


def suggest_solution(message):
    """
    Sugere soluções para problemas comuns
    
    Args:
        message: Mensagem do usuário
        
    Returns:
        Sugestão de solução ou None
    """
    match = re.match(r"Sugerir solução para (.+)", message)
    if match:
        problem = match.group(1).lower()
        solutions = {
            "computador não liga": "Verifique a fonte de energia e reinicie o dispositivo.",
            "internet lenta": "Reinicie o roteador e verifique a conexão.",
            "configurar uma vpn": "Acesse as configurações de rede e insira as credenciais da VPN fornecidas pelo TI."
        }
        return solutions.get(problem, "Desculpe, não tenho uma solução para esse problema no momento.")
    return None
