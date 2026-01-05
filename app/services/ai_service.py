import os
from google import genai
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class OraculoAI:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Erro ao inicializar cliente Gemini: {e}")

    def generate_response(self, user_message, context=""):
        """
        Gera uma resposta usando o Gemini (via google-genai SDK).
        Retorna None se a API não estiver configurada ou falhar.
        """
        if not self.client:
            return None

        try:
            system_prompt = """
            Você é o Oráculo Nexus, uma inteligência artificial avançada e guardiã do conhecimento de TI.
            Sua persona é sábia, futurista, levemente enigmática mas extremamente útil.
            
            Diretrizes:
            1. Responda de forma concisa e direta, mas com um tom "cyberpunk/tech".
            2. Use formatação Markdown (negrito, listas, código) para estruturar a resposta.
            3. Se a pergunta for técnica, dê a solução passo a passo.
            4. Se não souber a resposta, admita com elegância (ex: "Meus bancos de dados não contêm essa informação no momento").
            5. Mantenha o contexto de suporte técnico (TI, Hardware, Software, Redes).
            
            Contexto Adicional:
            {context}
            """
            
            full_prompt = f"{system_prompt}\n\nUsuário: {user_message}\nOráculo:"
            
            response = self.client.models.generate_content(
                model='gemini-flash-latest',
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            print(f"Erro na API do Gemini: {e}")
            return None

# Instância global
ai_service = OraculoAI()
