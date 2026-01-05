# 📁 Estrutura de Arquivos - Service Desk Chat Moderno

## Arquivos na Raiz

### Arquivos Principais
- **app.py** - Aplicação Flask principal (modularizada)
- **app_original.py** - Backup do arquivo original (2554 linhas)
- **run.py** - Ponto de entrada alternativo

### Configuração
- **requirements.txt** - Dependências Python para produção
- **requirements_local.txt** - Dependências Python para desenvolvimento local
- **Procfile** - Configuração para deploy no Heroku
- **README.markdown** - Documentação principal do projeto

### Diretórios

#### 📦 `app/` - Código da Aplicação
Código modularizado da aplicação:
- `models/` - 9 arquivos de modelos do banco de dados
- `routes/` - Blueprints de rotas (em desenvolvimento)
- `utils/` - 4 módulos de funções utilitárias
- `config.py` - Configurações centralizadas
- `extensions.py` - Extensões Flask
- `forms.py` - Formulários

#### 🎨 `templates/` - Templates HTML
Templates organizados em 10 subpastas por funcionalidade

#### 🎯 `static/` - Arquivos Estáticos
CSS, JavaScript e imagens

#### 💾 `data/` - Dados JSON
5 arquivos JSON com dados de demonstração

#### 🔧 `scripts/` - Scripts Utilitários
4 scripts Python para tarefas administrativas

#### 📚 `docs/` - Documentação
- `ESTRUTURA.md` - Guia da estrutura do projeto
- `MELHORIAS_IMPLEMENTADAS.md` - Histórico de melhorias
- `todo.md` - Lista de tarefas pendentes

#### 🗄️ `instance/` - Banco de Dados
Banco de dados SQLite (gerado automaticamente)

## Resumo da Organização

```
Raiz (7 arquivos essenciais)
├── app/              # Código modularizado
├── templates/        # HTML organizados
├── static/           # CSS, JS, imagens
├── data/             # JSON de dados
├── scripts/          # Utilitários Python
├── docs/             # Documentação
└── instance/         # Banco de dados
```

**Total:** 7 arquivos na raiz + 7 diretórios organizados
