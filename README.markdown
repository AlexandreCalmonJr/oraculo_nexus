# 🔮 Oráculo Nexus

> **"Onde o Conhecimento Encontra o Futuro."**

Bem-vindo ao **Oráculo Nexus**, a revolução na aprendizagem gamificada. Esqueça as plataformas de ensino monótonas e estáticas. Aqui, cada aula é uma missão, cada dúvida é uma oportunidade de evoluir, e o seu mentor é uma Inteligência Artificial de última geração.

Combinando a estética imersiva **Cyberpunk** com o poder do **Google Gemini**, o Oráculo Nexus transforma o ato de estudar em uma jornada épica. Junte-se a guildas, derrote Bosses lendários e torne-se uma lenda no ranking global.

---

## 📚 Documentação Oficial

Para garantir que todos - de recrutas a mestres - tenham a melhor experiência, preparamos guias detalhados:

-   👨‍💻 **[Guia do Desenvolvedor](docs/developer_guide.md)**: Mergulhe no código. Entenda a arquitetura, configure seu ambiente e contribua para o Nexus.
-   🎓 **[Guia do Aluno](docs/student_guide.md)**: Seu manual de sobrevivência. Aprenda a usar o Chatbot, completar desafios e subir de nível.
-   🛡️ **[Guia do Administrador](docs/admin_guide.md)**: Para os mestres do jogo. Gerencie usuários, crie desafios épicos e mantenha a ordem no sistema.

---

## ✨ Funcionalidades Principais

### 🤖 O Oráculo (AI Chat)
O coração da plataforma. Um assistente inteligente alimentado pelo **Google Gemini** que não apenas responde às suas dúvidas, mas atua como um mentor.
-   **Respostas Contextuais:** Entende o contexto do seu curso.
-   **Sugestões de Desafios:** Recomenda missões baseadas nas suas perguntas para ganhar XP extra.
-   **Personalidade Única:** Interaja com uma IA com personalidade própria.

### 🎮 Gamificação Profunda
Transforme o estudo numa jornada de RPG:
-   **XP e Níveis:** Ganhe experiência por cada interação e suba de nível.
-   **Boss Fights:** Junte-se ao seu time para derrotar desafios complexos em tempo real.
-   **Conquistas:** Desbloqueie medalhas exclusivas.
-   **Ranking:** Compita globalmente ou entre times.

### 🎨 Design Imersivo
Uma interface moderna e responsiva com estética **Cyberpunk**:
-   Efeitos de Glassmorphism (Vidro Fosco).
-   Animações fluidas e interativas.
-   Modo Dark nativo com acentos em Neon (Cyan/Purple).

---

## 🛠️ Instalação Rápida

### Pré-requisitos
-   Python 3.8+
-   Chave de API do Google Gemini

### 1. Clone o Repositório
```bash
git clone https://github.com/AlexandreCalmonJr/oraculo_nexus.git
cd oraculo_nexus
```

### 2. Ambiente Virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Dependências
```bash
pip install -r requirements.txt
```

### 4. Configuração (.env)
Crie um arquivo `.env` na raiz:
```env
SECRET_KEY=sua_chave_secreta
DATABASE_URL=sqlite:///nexus.db
GOOGLE_API_KEY=sua_chave_gemini_aqui
```

### 5. Executar
```bash
flask run
```
Acesse: `http://127.0.0.1:5000`

---

## 🤝 Contribuição
Sinta-se livre para abrir Issues e Pull Requests para expandir o Nexus.