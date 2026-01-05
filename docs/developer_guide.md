# 💻 Guia do Desenvolvedor - Oráculo Nexus

Bem-vindo à documentação técnica do **Oráculo Nexus**. Este guia foi desenhado para ajudar você a configurar o ambiente, entender a arquitetura e contribuir para o projeto.

## 🏗️ Arquitetura do Projeto

O Oráculo Nexus é construído sobre uma arquitetura MVC (Model-View-Controller) utilizando **Flask** (Python).

### Estrutura de Diretórios
-   `app.py`: O ponto de entrada da aplicação. Configura o app Flask, extensões e registra os blueprints.
-   `models.py`: Definições das tabelas da base de dados (SQLAlchemy).
-   `routes/`: Contém a lógica das rotas (Controllers).
    -   `auth_routes.py`: Login, registro e autenticação.
    -   `user_routes.py`: Dashboard do aluno, perfil.
    -   `admin_routes.py`: Painel administrativo.
    -   `chat_routes.py`: Lógica do Chatbot e integração com Gemini AI.
-   `templates/`: Arquivos HTML (Jinja2).
-   `static/`: CSS, JavaScript e imagens.

## 🛠️ Configuração do Ambiente de Desenvolvimento

### Pré-requisitos
-   Python 3.8 ou superior
-   Git
-   Uma chave de API do Google Gemini (Google AI Studio)

### Passo a Passo

1.  **Clone o Repositório**
    ```bash
    git clone https://github.com/AlexandreCalmonJr/oraculo_nexus.git
    cd oraculo_nexus
    ```

2.  **Crie o Ambiente Virtual**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Instale as Dependências**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as Variáveis de Ambiente**
    Crie um arquivo `.env` na raiz do projeto:
    ```env
    SECRET_KEY=dev_key_123
    DATABASE_URL=sqlite:///nexus.db
    GOOGLE_API_KEY=sua_chave_aqui
    ```

5.  **Inicialize o Banco de Dados**
    A aplicação cria as tabelas automaticamente na primeira execução.
    Para criar um admin inicial:
    ```bash
    flask create-admin --name "Admin" --email "admin@nexus.com" --password "admin"
    ```

6.  **Execute o Servidor**
    ```bash
    flask run --debug
    ```

## 🧩 Componentes Chave

### Integração com IA (Gemini)
A lógica de IA reside em `routes/chat_routes.py`. Utilizamos a biblioteca `google-generativeai` para enviar o contexto do aluno e receber respostas personalizadas.
**Dica:** Ao modificar o prompt do sistema, teste exaustivamente para garantir que o "Oráculo" mantenha sua persona.

### Sistema de Gamificação
Os modelos `User`, `Challenge`, `Team` e `Achievement` em `models.py` formam o núcleo da gamificação.
-   **XP e Níveis:** A lógica de cálculo de nível está no método `User.update_level()`.

## 🤝 Como Contribuir

1.  Faça um Fork do projeto.
2.  Crie uma Branch para sua feature (`git checkout -b feature/NovaFeature`).
3.  Commit suas mudanças (`git commit -m 'Add some NovaFeature'`).
4.  Push para a Branch (`git push origin feature/NovaFeature`).
5.  Abra um Pull Request.

---
*Happy Coding!* 🚀
