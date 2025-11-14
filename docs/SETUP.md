# 🔧 Setup Guide - Agente Naval WhatsApp

Guia passo a passo para configurar a automação de WhatsApp localmente e preparar para produção.

## 📋 Pré-requisitos

- **Python 3.11+** (verificar com `python --version`)
- **PostgreSQL 14+** (ou Docker)
- **Git** configurado
- **Conta OpenAI** com API key
- **Conta Evolution API** com instância ativa
- **GitHub** para controle de versão

## 🚀 Setup Local (Desenvolvimento)

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/agentenaval.git
cd agentenaval
```

### 2. Criar Arquivo .env

```bash
cp .env.example .env
```

Editar `.env` com suas credenciais:

```bash
# Database (usando PostgreSQL local)
DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/agentenaval

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

# Segurança (gerar tokens aleatórios)
WEBHOOK_SECRET=seu-token-super-seguro-min-32-chars
SECRET_KEY=sua-chave-super-secreta

# Emails (opcional para desenvolvimento)
ALERT_EMAIL=seu-email@empresa.com
SMTP_USER=seu-email@gmail.com
SMTP_PASS=sua-app-password

# Ambiente
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

### 3. Criar Virtual Environment

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Linux/Mac)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate
```

### 4. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 5. Configurar Banco de Dados

**Opção A: PostgreSQL Local**

```bash
# Criar usuário e banco (no psql)
createuser agentenaval -P  # Digite sua senha
createdb agentenaval -O agentenaval
```

**Opção B: Docker (Recomendado)**

```bash
docker-compose up -d postgres
```

### 6. Rodar Migrations

```bash
# Garantir que DATABASE_URL está configurada
alembic upgrade head
```

### 7. Iniciar a Aplicação

```bash
# Modo desenvolvimento com reload automático
python -m flask --app src.app run --debug

# Ou usar Gunicorn
gunicorn --bind 0.0.0.0:5000 src.wsgi:app
```

Acessar em `http://localhost:5000`

## 🐳 Setup com Docker Compose (Recomendado)

Mais fácil e consistente entre ambientes.

### 1. Criar .env

```bash
cp .env.example .env
# Editar com suas credenciais
```

### 2. Iniciar Containers

```bash
docker-compose up --build
```

O comando vai:
- Criar e iniciar PostgreSQL
- Instalar dependências Python
- Rodar migrations automáticamente
- Iniciar Flask app na porta 5000

### 3. Verificar Saúde

```bash
# Health check
curl http://localhost:5000/health

# Deve retornar:
# {"status":"healthy","timestamp":"...","version":"1.0.0","database":"connected"}
```

### 4. Para de verdade

```bash
docker-compose down
```

## 🔌 Configurar Evolution API

### 1. Setup Inicial

1. Acesse https://evolution-api.com
2. Crie uma nova instância
3. Configure webhook para: `https://seu-dominio.com/api/webhooks/evolution`
4. Gere API Key e copie para `.env`

### 2. Testar Conexão

```bash
# Verificar conexão com webhook
curl -X GET http://localhost:5000/api/webhooks/evolution \
  -H "Authorization: Bearer seu-webhook-secret"
```

### 3. Validar Webhook

```python
# Script para teste local
import requests
import json

webhook_payload = {
    "event": "messages.upsert",
    "data": {
        "instanceId": "sua-instance",
        "messages": [{
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False,
                "id": "TEST123"
            },
            "message": {
                "conversation": "Olá, tudo bem?"
            }
        }]
    }
}

response = requests.post(
    "http://localhost:5000/api/webhooks/evolution",
    json=webhook_payload,
    headers={"Authorization": "Bearer seu-webhook-secret"}
)

print(response.status_code, response.json())
```

## 🔑 Configurar OpenAI

### 1. Obter API Key

1. Vá para https://platform.openai.com/api-keys
2. Crie nova chave
3. Copie para `OPENAI_API_KEY` em `.env`

### 2. Testar Chamada

```python
# Script de teste
from src.services.openai_agent import OpenAIAgent

agent = OpenAIAgent()
response, metadata = agent.generate_response(
    user_message="Olá! Gostaria de abrir uma franquia em São Paulo",
    lead_id="test-lead"
)

print("Resposta:", response)
print("Tokens:", metadata['tokens_total'])
print("Custo:", metadata['cost_usd'])
```

## 🧪 Rodar Testes

### Testes Unitários

```bash
# Todos os testes
pytest

# Apenas unit tests
pytest tests/unit/

# Com coverage
pytest --cov=src tests/
```

### Testes E2E

```bash
# Apenas E2E
pytest -m e2e

# Verbose
pytest -m e2e -v
```

## 📊 Monitorar Custos OpenAI

Executar diariamente para verificar uso:

```bash
python scripts/check_openai_usage.py
```

Retorna:
- Uso acumulado do mês
- Percentual do limite
- Alertas se atingir 50%, 80%, 100%

## 🔍 Verificar Logs

### Desenvolvimento (stdout)

Os logs aparecem no terminal onde rodou `flask run`

### Produção (JSON)

Logs em formato JSON para integração com ELK/CloudWatch:

```bash
# Ver logs recentes
tail -f logs/app.log | jq .
```

## 🚨 Troubleshooting

### Erro de conexão com PostgreSQL

```bash
# Verificar se PostgreSQL está rodando
psql -U agentenaval -d agentenaval -c "SELECT 1"

# Com Docker
docker-compose logs postgres
```

### Erro de API Key OpenAI

```bash
# Verificar chave em .env
echo $OPENAI_API_KEY

# Testar conexão
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

### Webhook não recebendo mensagens

1. Verificar URL do webhook em Evolution API
2. Verificar WEBHOOK_SECRET está correto
3. Ver logs: `curl http://localhost:5000/health`

## 📝 Próximos Passos

1. **Configurar Evolution API**: Apontar webhook e testar
2. **Testar Agente**: Enviar mensagens de teste
3. **Monitorar Custos**: Rodar check_openai_usage.py regularmente
4. **Deploy**: Ver [DEPLOYMENT.md](./DEPLOYMENT.md)

---

**Precisa de ajuda?** Abra uma issue no GitHub ou consulte a documentação completa em `docs/`
