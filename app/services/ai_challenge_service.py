"""
Serviço de IA para Desafios
Fornece validação inteligente, feedback personalizado e geração de dicas
"""
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()


class AIChallengeService:
    """Serviço de IA especializado em desafios"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Erro ao inicializar cliente Gemini: {e}")
    
    def validate_answer(self, challenge, user_answer, use_ai=True):
        """
        Valida resposta do usuário de forma inteligente
        
        Args:
            challenge: Objeto Challenge
            user_answer: Resposta do usuário
            use_ai: Se True, usa IA para validação semântica
            
        Returns:
            dict: {
                'is_correct': bool,
                'confidence': float (0-1),
                'explanation': str
            }
        """
        # Validação exata (fallback)
        expected = challenge.expected_answer.strip().lower()
        user_ans = user_answer.strip().lower()
        
        if expected == user_ans:
            return {
                'is_correct': True,
                'confidence': 1.0,
                'explanation': 'Resposta exata!'
            }
        
        # Validação com IA (semântica)
        if use_ai and self.client:
            try:
                prompt = f"""
                Você é um avaliador de respostas técnicas. Analise se a resposta do usuário está correta.
                
                **Desafio:** {challenge.title}
                **Descrição:** {challenge.description}
                **Resposta Esperada:** {challenge.expected_answer}
                **Resposta do Usuário:** {user_answer}
                
                Avalie se a resposta do usuário está:
                1. Completamente correta (mesmo que com palavras diferentes)
                2. Parcialmente correta
                3. Incorreta
                
                Responda APENAS no formato JSON:
                {{
                    "is_correct": true/false,
                    "confidence": 0.0-1.0,
                    "explanation": "explicação breve"
                }}
                """
                
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=prompt
                )
                
                # Parse JSON da resposta
                import json
                result_text = response.text.strip()
                
                # Remover markdown code blocks se existirem
                if result_text.startswith('```'):
                    result_text = result_text.split('```')[1]
                    if result_text.startswith('json'):
                        result_text = result_text[4:]
                    result_text = result_text.strip()
                
                result = json.loads(result_text)
                return result
                
            except Exception as e:
                print(f"Erro na validação com IA: {e}")
                # Fallback para validação simples
                return {
                    'is_correct': False,
                    'confidence': 0.5,
                    'explanation': 'Não foi possível validar com IA. Tente novamente.'
                }
        
        # Se não usar IA ou falhar
        return {
            'is_correct': False,
            'confidence': 0.3,
            'explanation': 'Resposta não corresponde exatamente à esperada.'
        }
    
    def generate_feedback(self, challenge, user_answer, is_correct):
        """
        Gera feedback personalizado baseado na resposta
        
        Args:
            challenge: Objeto Challenge
            user_answer: Resposta do usuário
            is_correct: Se a resposta está correta
            
        Returns:
            str: Feedback personalizado
        """
        if not self.client:
            if is_correct:
                return "✅ Parabéns! Resposta correta!"
            return "❌ Resposta incorreta. Tente novamente!"
        
        try:
            prompt = f"""
            Você é o Oráculo Nexus, um mentor de TI cyberpunk.
            
            **Desafio:** {challenge.title}
            **Descrição:** {challenge.description}
            **Resposta Esperada:** {challenge.expected_answer}
            **Resposta do Usuário:** {user_answer}
            **Status:** {"CORRETA" if is_correct else "INCORRETA"}
            
            Gere um feedback personalizado e motivador:
            - Se CORRETA: Parabenize de forma épica e explique por que está certa
            - Se INCORRETA: Seja encorajador, dê uma dica sutil sem entregar a resposta
            
            Use emojis e formatação Markdown. Máximo 3 linhas.
            """
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"Erro ao gerar feedback: {e}")
            if is_correct:
                return "✅ **Excelente!** Você dominou este desafio!"
            return "❌ **Quase lá!** Revise o conceito e tente novamente."
    
    def generate_hint(self, challenge, user_attempts=0):
        """
        Gera dica contextual baseada no desafio
        
        Args:
            challenge: Objeto Challenge
            user_attempts: Número de tentativas do usuário
            
        Returns:
            str: Dica personalizada
        """
        # Se já tem hint cadastrada, retornar
        if challenge.hint and user_attempts == 0:
            return challenge.hint
        
        if not self.client:
            return challenge.hint or "💡 Releia a descrição do desafio com atenção."
        
        try:
            difficulty = "sutil" if user_attempts < 2 else "mais direta"
            
            prompt = f"""
            Você é o Oráculo Nexus. Gere uma dica {difficulty} para este desafio:
            
            **Desafio:** {challenge.title}
            **Descrição:** {challenge.description}
            **Resposta Esperada:** {challenge.expected_answer}
            **Tentativas do Usuário:** {user_attempts}
            
            Regras:
            - Não dê a resposta direta
            - Use analogias ou exemplos
            - Seja encorajador
            - Máximo 2 linhas
            - Use emoji 💡 no início
            """
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"Erro ao gerar dica: {e}")
            return challenge.hint or "💡 Pense nos conceitos fundamentais relacionados ao tema."
    
    def generate_challenge(self, topic, difficulty='medium', challenge_type='text'):
        """
        Gera um novo desafio usando IA
        
        Args:
            topic: Tópico do desafio (ex: "Python", "Redes", "Linux")
            difficulty: Dificuldade ('easy', 'medium', 'hard')
            challenge_type: Tipo do desafio ('text', 'code', 'multiple_choice')
            
        Returns:
            dict: Dados do desafio gerado
        """
        if not self.client:
            return None
        
        try:
            difficulty_map = {
                'easy': 'iniciante (conceitos básicos)',
                'medium': 'intermediário (aplicação prática)',
                'hard': 'avançado (cenários complexos)'
            }
            
            prompt = f"""
            Você é o Oráculo Nexus, criador de desafios técnicos.
            
            Crie um desafio de **{topic}** nível **{difficulty_map.get(difficulty, 'médio')}**.
            
            Formato JSON:
            {{
                "title": "Título curto e atrativo",
                "description": "Descrição clara do desafio (2-3 linhas)",
                "expected_answer": "Resposta esperada",
                "hint": "Dica sutil",
                "points_reward": 10-50 (baseado na dificuldade),
                "level_required": "Iniciante/Intermediário/Avançado"
            }}
            
            O desafio deve ser:
            - Prático e relevante para TI
            - Claro e objetivo
            - Educativo
            """
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            
            # Parse JSON
            import json
            result_text = response.text.strip()
            
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            challenge_data = json.loads(result_text)
            challenge_data['challenge_type'] = challenge_type
            
            return challenge_data
            
        except Exception as e:
            print(f"Erro ao gerar desafio: {e}")
            return None


# Instância global
ai_challenge_service = AIChallengeService()
