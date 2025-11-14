# 🚀 Deployment Guide - Railway

Guia completo para fazer deploy da aplicação Agente Naval no Railway.

## 📋 Pré-requisitos

- Conta GitHub (código já deve estar pushado)
- Conta Railway (https://railway.app)
- OpenAI API Key
- Evolution API credenciais
- Email para alertas (opcional)

## 🚀 Deploy em 5 Minutos

### 1. Conectar GitHub ao Railway

1. Ir para https://railway.app e fazer login
2. Clicar em "New Project"
3. Selecionar "Deploy from GitHub"
4. Autorizar Railway a acessar seu GitHub
5. Selecionar repositório `agentenaval`

### 2. Configurar PostgreSQL Addon

Railroad vai detectar Dockerfile automaticamente.

Para adicionar PostgreSQL:

1. No painel do Railway, clicar em "Add Service"
2. Selecionar "PostgreSQL"
3. Aguardar provisionamento

O banco será criado automaticamente com variável `DATABASE_URL`.

### 3. Definir Variáveis de Ambiente

No painel do Railway, ir para "Variables" e adicionar:

```
# OpenAI
OPENAI_API_KEY=sk-seu-api-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.7
OPENAI_COST_LIMIT_MONTHLY=20

# Evolution API
EVOLUTION_API_URL=https://sua-instance.evolution-api.com
EVOLUTION_API_KEY=sua-api-key
EVOLUTION_INSTANCE_ID=sua-instance-id

# Segurança
WEBHOOK_SECRET=seu-token-super-seguro-min-32-chars
SECRET_KEY=sua-chave-super-secreta

# Regiões
ELIGIBLE_REGIONS=RS,SC,PR,SP,RJ,MG,ES,GO,MT,MS,DF
INTEREST_REGIONS=BA,PE,CE,RN,PB,AL,SE,PI,MA,AP,AM,RR,AC,TO

# Email (para alertas)
ALERT_EMAIL=seu-email@empresa.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASS=sua-app-password

# Ambiente
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 4. Deploy

Salvar variáveis e Railway vai fazer deploy automaticamente:

1. Construir imagem Docker
2. Provisionar banco de dados
3. Rodar migrations (Alembic)
4. Iniciar aplicação

Pode verificar progresso em "Logs".

### 5. Testar Deploy

```bash
# Health check (substituir com seu domínio Railway)
curl https://seu-projeto.up.railway.app/health

# Retorno esperado:
# {"status":"healthy","database":"connected"}
```

## 🔧 Configurar Domain Customizado (Opcional)

1. No painel Railway, clicar no serviço web
2. Em "Networking", clicar "Generate Domain" ou adicionar domain customizado
3. Apontar DNS do seu domínio para Railway

## 🔐 Segurança em Produção

### 1. Gerar Tokens Aleatórios

```bash
# Gerar WEBHOOK_SECRET
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Gerar SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Verificar HTTPS

Railway fornece HTTPS automaticamente. Verificar:

```bash
curl -I https://seu-projeto.up.railway.app/health
# Deve retornar 200 OK com HTTPS
```

### 3. Limpar Logs Sensíveis

Verificar que logs não contêm:
- API Keys
- Senhas
- Tokens privados

Railroad não loga esses dados por padrão (ver `src/utils/logging.py`).

## 📊 Monitoramento em Produção

### 1. Health Check Automático

Railway configura health check automaticamente no Dockerfile:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
```

Se falhar 3 vezes, Railway reinicia a aplicação.

### 2. Acessar Logs

```bash
# No painel Railway
# Serviço → Logs → filtrar por "ERROR" ou "CRITICAL"

# Via CLI
railway logs -f  # follow (tail -f)
```

### 3. Status Endpoint

```bash
curl https://seu-projeto.up.railway.app/api/admin/usage
```

Retorna estatísticas de uso, custos, leads, etc.

## 💰 Monitoramento de Custos

### 1. Script Automático

Rodar daily via cron:

```bash
# No Railway, adicionar "job" para rodar diariamente
python scripts/check_openai_usage.py
```

### 2. Alertas Automáticos

O script envia email quando atingir:
- 50% do limite → WARNING
- 80% do limite → CRITICAL
- 100% → BLOQUEIO

Verificar configuração SMTP está correta.

## 🔄 Deploy Contínuo (CI/CD)

### GitHub Actions (Automático)

Railway integra com GitHub automaticamente:

1. Cada push em `main` dispara deploy
2. Cada push em `develop` dispara para staging (opcional)
3. PRs rodam testes automáticamente

Ver `.github/workflows/` para configuração.

## 📝 Checklist pré-produção

- [ ] Variáveis de ambiente configuradas
- [ ] OpenAI API Key válida
- [ ] Evolution API conectada
- [ ] PostgreSQL addon criado
- [ ] Domain ou URL Railway acessível
- [ ] Health check passando (`/health`)
- [ ] Webhook recebendo mensagens da Evolution
- [ ] Logs em formato JSON
- [ ] HTTPS habilitado
- [ ] Alertas de custo configurados
- [ ] Backup de banco de dados habilitado (Railway faz automaticamente)

## 🚨 Troubleshooting

### Deploy falha

```bash
# Ver logs detalhados
railway logs -f

# Procurar por erros em:
# - DATABASE_URL inválida
# - API Keys faltando
# - Migrations falhando
```

### Webhook não funciona

1. Verificar URL: `https://seu-projeto.up.railway.app/api/webhooks/evolution`
2. Verificar WEBHOOK_SECRET em Evolution API
3. Ver logs: `railway logs -f | grep webhook`

### Custo alerta acionado

1. Verificar `/api/admin/usage` para detalhes
2. Aumentar `OPENAI_COST_LIMIT_MONTHLY` se necessário
3. Implementar cache de prompts (Fase 2)

### Database disco cheio

Railroad avisa se aproximar do limite. Opções:
1. Upgradar plano
2. Limpar logs antigos (manual)
3. Implementar limpeza automática

## 🔄 Rollback

Se deploy quebrou algo:

```bash
# Railway mantém histórico de deploys
# Painel → Deployments → selecionar versão anterior
```

## 📈 Escalando

Quando chegar a 50+ leads/dia:

1. **Aumentar workers**: `--workers 8` em Dockerfile
2. **Connection pooling**: Aumentar `SQLALCHEMY_POOL_SIZE`
3. **Cache**: Implementar Redis para cache de prompts
4. **Queue**: Usar Celery para processamento assíncrono

Detalhes em [Architecture Guide].

## 📚 Próximos Passos

1. **Testar em produção**: Enviar mensagens de teste
2. **Ativar monitoring**: Acompanhar logs e custos
3. **Fase 2**: Implementar follow-up automático (4 semanas)
4. **Fase 3**: Analytics e otimização (8+ semanas)

---

**Precisa de ajuda?** Ver [SETUP.md](./SETUP.md) ou abrir issue no GitHub.
