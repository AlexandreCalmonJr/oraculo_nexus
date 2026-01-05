# Service Desk Chat Moderno - Estrutura do Projeto

## 📁 Estrutura de Diretórios

```
service_desk_chat_moderno/
├── app/                        # Código da aplicação modularizado
│   ├── models/                 # Modelos do banco de dados (9 arquivos)
│   ├── routes/                 # Blueprints de rotas (em desenvolvimento)
│   ├── utils/                  # Funções utilitárias (4 módulos)
│   ├── __init__.py            # Factory da aplicação
│   ├── config.py              # Configurações centralizadas
│   ├── extensions.py          # Extensões Flask
│   ├── forms.py               # Formulários
│   └── legacy_routes.py       # Rotas temporárias (a migrar)
│
├── templates/                  # Templates HTML organizados
│   ├── admin/                 # Templates administrativos
│   ├── auth/                  # Login e registro
│   ├── boss_fights/           # Boss Fights
│   ├── challenges/            # Desafios
│   ├── chat/                  # Chat
│   ├── events/                # Eventos
│   ├── faq/                   # FAQs
│   ├── learning_paths/        # Trilhas de aprendizagem
│   ├── teams/                 # Equipes
│   └── user/                  # Dashboard, perfil, ranking
│
├── static/                     # Arquivos estáticos (CSS, JS, imagens)
├── data/                       # Arquivos de dados JSON
├── scripts/                    # Scripts utilitários Python
├── instance/                   # Banco de dados SQLite
│
├── app.py                      # Aplicação principal (modularizada)
├── app_original.py            # Backup do arquivo original
├── run.py                      # Ponto de entrada alternativo
├── requirements.txt           # Dependências Python
└── README.markdown            # Documentação do projeto
```

## 🚀 Como Executar

### Desenvolvimento
```bash
python app.py
```

### Produção (Heroku)
```bash
gunicorn app:app
```

## 📦 Módulos Principais

### Models (`app/models/`)
- `user.py` - Usuários e convites
- `gamification.py` - Níveis e conquistas
- `content.py` - Categorias e FAQs
- `challenges.py` - Desafios
- `teams.py` - Equipes e batalhas
- `boss_fights.py` - Boss Fights
- `learning_paths.py` - Trilhas de aprendizagem
- `events.py` - Eventos e caça ao tesouro
- `chat.py` - Chat e tickets

### Utils (`app/utils/`)
- `ticket_utils.py` - Processamento de tickets
- `faq_utils.py` - Busca e formatação de FAQs
- `gamification_utils.py` - Sistema de gamificação
- `file_utils.py` - Processamento de arquivos

### Routes (`app/routes/`)
- `auth.py` - Autenticação (parcial)
- `user.py` - Usuário (parcial)
- *(Outros blueprints em desenvolvimento)*

## 📝 Scripts Utilitários (`scripts/`)

- `create_test_user.py` - Criar usuários de teste
- `generate_invite_code.py` - Gerar códigos de convite
- `gerador_conteudo.py` - Gerar conteúdo de demonstração
- `populate_demo_data.py` - Popular banco com dados demo

## 📊 Dados (`data/`)

- `boss_fight.json` - Dados de Boss Fights
- `conteudo_cdz_python.json` - Conteúdo CDZ Python
- `desafios.json` - Desafios
- `faqs.json` - FAQs
- `trilha_python.json` - Trilha Python

## 🔧 Configuração

As configurações estão centralizadas em `app/config.py`. Configure as variáveis de ambiente:

- `SECRET_KEY` - Chave secreta do Flask
- `DATABASE_URL` - URL do banco de dados
- `CLOUDINARY_CLOUD_NAME` - Nome do cloud Cloudinary
- `CLOUDINARY_API_KEY` - API key Cloudinary
- `CLOUDINARY_API_SECRET` - API secret Cloudinary
- `REDIS_URL` - URL do Redis (opcional)

## 📚 Próximos Passos

1. Completar migração de rotas para blueprints
2. Atualizar referências de templates
3. Remover código legado (`app_original.py`)
4. Adicionar testes automatizados

## 🎯 Benefícios da Modularização

- ✅ Código organizado por responsabilidade
- ✅ Arquivos menores e mais focados
- ✅ Fácil manutenção e escalabilidade
- ✅ Melhor colaboração em equipe
- ✅ Estrutura preparada para crescimento
