FROM python:3.12-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baixar modelo do Spacy durante o build (Melhor performance e estabilidade)
RUN python -m spacy download pt_core_news_sm

# Copiar o resto do código
COPY . .

# Variáveis de ambiente padrão (podem ser sobrescritas pelo Railway)
ENV PORT=8080

# Comando de inicialização
CMD gunicorn run:app --workers 1 --timeout 120 --bind 0.0.0.0:$PORT
