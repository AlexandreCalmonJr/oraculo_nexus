# Guia de Configuração do PostgreSQL no Railway

## Problema Atual
```
psycopg2.OperationalError: connection to server at "postgres.railway.internal" failed
```

Isso significa que o banco de dados PostgreSQL não está configurado ou não está acessível.

## Solução: Configurar PostgreSQL no Railway

### Opção 1: Adicionar PostgreSQL ao Projeto (Recomendado)

1. **Acesse o Dashboard do Railway**
   - Vá para: https://railway.app/dashboard
   - Selecione seu projeto "oraculo_nexus"

2. **Adicionar PostgreSQL**
   - Clique em "+ New"
   - Selecione "Database"
   - Escolha "PostgreSQL"
   - Clique em "Add PostgreSQL"

3. **Conectar ao Serviço**
   - O Railway vai criar automaticamente as variáveis de ambiente
   - Aguarde alguns segundos para o banco inicializar

4. **Verificar Variáveis de Ambiente**
   - Vá em "Variables" no seu serviço web
   - Verifique se existe `DATABASE_URL`
   - Se não existir, copie de "Connect" no PostgreSQL

### Opção 2: Usar SQLite (Alternativa Simples)

Se você preferir usar SQLite ao invés de PostgreSQL:

1. **Modificar app/__init__.py**
   - Mudar a configuração do banco de dados

2. **Remover psycopg2-binary do requirements.txt**
   - Não é necessário para SQLite

## Verificação

Após adicionar o PostgreSQL, o Railway vai:
1. ✅ Criar o banco de dados
2. ✅ Configurar as variáveis de ambiente automaticamente
3. ✅ Reiniciar o serviço
4. ✅ Criar as tabelas automaticamente (via db.create_all())

## Próximos Passos

1. Adicione o PostgreSQL no Railway
2. Aguarde o deploy completar
3. Verifique os logs para confirmar que conectou

## Comandos Úteis

Para verificar se o banco está funcionando:
```bash
railway logs
```

Para acessar o PostgreSQL diretamente:
```bash
railway run psql $DATABASE_URL
```
