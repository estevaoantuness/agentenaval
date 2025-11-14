# 🚀 Agente Naval - Automação de WhatsApp para Franquias

Sistema inteligente de triagem e qualificação de leads via WhatsApp usando Claude/OpenAI, Evolution API e PostgreSQL.

## 📋 Visão Geral

**Agente Naval** é um assistente de WhatsApp empresarial que:

- ✅ Recebe leads em tempo real via WhatsApp
- ✅ Realiza triagem automática e coleta de informações
- ✅ Valida elegibilidade regional
- ✅ Agenda reuniões com vendedores
- ✅ Monitora custos OpenAI automaticamente
- ✅ Mantém histórico estruturado em PostgreSQL
- ✅ Oferece logging centralizado para análise

**Volume esperado:** 15 leads/dia (aproximadamente 450/mês)

## 🛠️ Stack Tecnológica

| Componente | Tecnologia |
|-----------|-----------|
| **Backend** | Flask (Python 3.11+) |
| **IA/NLP** | OpenAI GPT-4o-mini |
| **WhatsApp** | Evolution API |
| **Banco de Dados** | PostgreSQL |
| **Scheduler** | APScheduler |
| **Deploy** | Railway |
| **Testing** | pytest + pytest-cov |
| **Logging** | structlog |

## 📁 Estrutura do Projeto

```
agentenaval/
├── src/
│   ├── app.py                 # Flask principal
│   ├── config.py              # Configuração e validação de env vars
│   ├── models/                # SQLAlchemy models
│   │   ├── lead.py
│   │   ├── conversation.py
│   │   └── scheduling.py
│   ├── services/              # Lógica de negócio
│   │   ├── openai_agent.py    # Integração com OpenAI
│   │   ├── evolution_api.py   # Integração com Evolution
│   │   ├── lead_screening.py  # Triagem e qualificação
│   │   ├── cost_monitor.py    # Monitoramento de custo
│   │   └── scheduler.py       # Follow-up automático
│   ├── api/                   # Rotas Flask
│   │   ├── webhooks.py        # Webhook Evolution API
│   │   ├── health.py          # Health check
│   │   └── admin.py           # Endpoints de admin (monitoramento)
│   ├── schemas/               # Pydantic models para validação
│   │   └── payloads.py
│   ├── utils/                 # Funções auxiliares
│   │   ├── logging.py         # Setup de logging estruturado
│   │   ├── validators.py      # Validadores customizados
│   │   └── security.py        # Funções de segurança
│   └── prompts/               # System prompts (carregados em runtime)
│
├── database/
│   └── migrations/            # Alembic migrations
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
│
├── tests/
│   ├── unit/                  # Testes unitários
│   │   ├── test_lead_screening.py
│   │   ├── test_validators.py
│   │   └── test_services.py
│   ├── integration/           # Testes de integração
│   │   └── test_database.py
│   ├── e2e/                   # Testes end-to-end
│   │   └── test_flows.py
│   └── fixtures/              # Mocks e fixtures
│       └── payloads.py
│
├── prompts/
│   └── v1.0/                  # Versão 1.0 dos prompts
│       ├── system.txt         # Persona base
│       ├── triagem.txt        # Prompt de triagem
│       ├── objecoes.txt       # Contorno de objeções
│       ├── agendamento.txt    # Coleta de dados de reunião
│       └── metadata.json      # Metadados da versão
│
├── scripts/
│   ├── check_openai_usage.py  # Script de monitoramento de custo
│   └── local_webhook_test.py  # Teste local de webhook
│
├── docs/
│   ├── API.md                 # Documentação de API
│   ├── SETUP.md               # Instruções de setup
│   ├── DEPLOYMENT.md          # Deploy no Railway
│   ├── PROMPTS.md             # Versionamento de prompts
│   └── TESTING.md             # Guia de testes
│
├── .github/workflows/
│   ├── ci.yml                 # CI (testes)
│   └── deploy.yml             # Deploy automático
│
├── .gitignore
├── .env.example               # Variáveis de ambiente (exemplo)
├── requirements.txt           # Dependências Python
├── Dockerfile                 # Container production
├── docker-compose.yml         # Setup local com Docker
├── pytest.ini                 # Configuração pytest
└── README.md                  # Este arquivo
```

## 🚀 Quick Start

### 1. Pré-requisitos

- Python 3.11+
- PostgreSQL 14+
- Docker & Docker Compose (opcional)
- Conta OpenAI (GPT-4o-mini)
- Conta Evolution API

### 2. Setup Local

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/agentenaval.git
cd agentenaval

# Crie arquivo .env com suas credenciais
cp .env.example .env
# Edite .env com suas chaves (OpenAI, Evolution API, Database URL, etc)

# Crie virtual environment
python -m venv venv
source venv/bin/activate  # no Windows: venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt

# Rode migrations do banco de dados
alembic upgrade head

# Inicie a aplicação
python -m flask --app src.app run
```

### 3. Com Docker Compose

```bash
# Inicie PostgreSQL + aplicação
docker-compose up --build

# Acesse em http://localhost:5000
```

## 🔑 Configuração das Integrações

### OpenAI API

1. Crie conta em https://platform.openai.com
2. Gere API Key em https://platform.openai.com/account/api-keys
3. Adicione à variável `OPENAI_API_KEY` em `.env`

### Evolution API

1. Configure instância em https://evolution-api.com/
2. Obtenha URL da instância e API Key
3. Crie webhook apontando para: `https://seu-dominio.com/api/webhooks/evolution`
4. Configure `EVOLUTION_API_URL` e `EVOLUTION_API_KEY` em `.env`

### PostgreSQL

```bash
# Local (sem Docker)
createdb agentenaval
# Ou use Railway addon (automático)
```

## 📊 Fluxo de Funcionamento

```
Lead entra no WhatsApp
     ↓
Webhook recebe mensagem
     ↓
Validação (auth, rate limit)
     ↓
Consulta OpenAI (triagem)
     ↓
Salva conversa no DB
     ↓
Resposta automática (< 3s)
     ↓
Coleta dados (nome, região, interesse)
     ↓
Valida região (elegível/interesse)
     ↓
Se elegível: Agenda reunião → Status: agendado
Se não: Registra para análise → Status: não_elegível
     ↓
Notifica vendedor
```

## 🧪 Testes

```bash
# Rodar todos os testes
pytest

# Com cobertura
pytest --cov=src tests/

# Apenas E2E
pytest tests/e2e/

# Apenas unit
pytest tests/unit/

# Modo verbose
pytest -v
```

## 📈 Monitoramento de Custo

Script automático que consulta uso OpenAI:

```bash
# Executar manualmente
python scripts/check_openai_usage.py

# Em produção: roda diariamente via cron
```

Alertas automáticos em:
- 50% do limite mensal (WARNING)
- 80% do limite mensal (CRITICAL)
- 100% do limite mensal (BLOQUEIO)

## 🔐 Segurança

- ✅ Autenticação de webhook com Bearer Token/HMAC
- ✅ Rate limiting (30 req/min por phone, 100 req/min global)
- ✅ Validação de inputs com Pydantic
- ✅ HTTPS obrigatório em produção
- ✅ Secrets em variáveis de ambiente

## 📚 Documentação Completa

- [API.md](docs/API.md) - Endpoints e payloads
- [SETUP.md](docs/SETUP.md) - Instruções de configuração
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Deploy no Railway
- [PROMPTS.md](docs/PROMPTS.md) - Versionamento de prompts
- [TESTING.md](docs/TESTING.md) - Guia de testes

## 🎯 Roadmap

### MVP (v1.0) ✅
- [x] Recepção de leads
- [x] Triagem automática
- [x] Validação regional
- [x] Agendamento
- [x] Monitoramento de custo
- [x] Testes E2E
- [x] Deploy Railway

### Fase 2 (v2.0) 🚧
- [ ] Follow-up automático com SLAs
- [ ] Estratégias de reengajamento
- [ ] Notificações para vendedores
- [ ] Dashboard básico

### Fase 3 (v3.0) 🔜
- [ ] Analytics regional
- [ ] A/B testing de prompts
- [ ] Otimização de custos
- [ ] Dashboard completo

## 💬 Suporte

Para dúvidas ou issues, abra uma issue no GitHub: https://github.com/seu-usuario/agentenaval/issues

## 📄 Licença

MIT License - veja LICENSE.md para detalhes

---

**Desenvolvido com ❤️ usando Claude Code**
