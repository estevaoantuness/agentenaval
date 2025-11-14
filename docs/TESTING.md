# 🧪 Testing Guide - Agente Naval

Guia completo de testes: unitários, integração e end-to-end.

## 📊 Cobertura de Testes

```
MVP Target: 80% code coverage

Cobertura esperada:
- Services: 85%+ (crítico)
- Utils: 90%+ (validadores)
- API: 75%+ (rotas)
- Models: 100% (rápido)
```

## 🚀 Quick Start

```bash
# Instalar dependências de teste
pip install -r requirements.txt

# Rodar todos os testes
pytest

# Com coverage
pytest --cov=src tests/

# Apenas E2E
pytest -m e2e

# Apenas unit
pytest -m unit
```

## 📋 Estrutura de Testes

```
tests/
├── __init__.py
├── conftest.py                # Fixtures compartilhadas
├── unit/                      # Testes unitários (rápidos)
│   ├── test_validators.py
│   ├── test_services.py
│   └── test_models.py
├── integration/               # Testes de integração (médios)
│   ├── test_database.py
│   └── test_api_endpoints.py
└── e2e/                       # Testes end-to-end (lentos)
    ├── test_flows.py
    └── test_webhook.py
```

## 🎯 Tipos de Testes

### Unit Tests (Rápidos)

Testam funções isoladas, sem dependências externas.

```python
# tests/unit/test_validators.py

@pytest.mark.unit
def test_validate_phone_valid():
    """Testa validação de telefone."""
    assert validate_phone("11999999999") is True
    assert validate_phone("invalid") is False
```

**Executar apenas unit:**
```bash
pytest tests/unit/ -v
pytest -m unit  # usando marker
```

### Integration Tests (Médios)

Testam integração entre componentes (ex: DB + API).

```python
# tests/integration/test_database.py

@pytest.mark.integration
def test_lead_creation_in_db(db):
    """Testa criação de lead no banco."""
    lead = Lead(phone="5511999999999")
    db.add(lead)
    db.commit()

    retrieved = db.query(Lead).filter_by(phone="5511999999999").first()
    assert retrieved is not None
```

**Executar apenas integration:**
```bash
pytest tests/integration/ -v
pytest -m integration
```

### End-to-End Tests (Lentos)

Testam fluxo completo: webhook → NLP → BD → resposta.

```python
# tests/e2e/test_flows.py

@pytest.mark.e2e
def test_flow_lead_elegivel_agendamento(client, db, mock_openai):
    """Testa fluxo completo de lead elegível."""
    # 1. Envia webhook
    # 2. Processa com OpenAI
    # 3. Verifica BD
    # 4. Valida resposta
```

**Executar apenas E2E:**
```bash
pytest tests/e2e/ -v
pytest -m e2e
```

## 🔧 Fixtures Disponíveis

### Fixtures Básicas

```python
@pytest.fixture
def app():
    """Aplicação Flask para testes."""
    from src.app import create_app
    app, db = create_app()
    return app

@pytest.fixture
def client(app):
    """Cliente Flask para fazer requisições."""
    return app.test_client()

@pytest.fixture
def db(app):
    """Sessão de banco de dados."""
    # Cria tabelas em memória
    # Limpa após teste
    return db
```

### Fixtures de Dados

```python
@pytest.fixture
def lead_data():
    """Dados de teste para lead."""
    return {
        "phone": "5511999999999",
        "nome": "João Silva",
        "regiao": "SP",
    }

@pytest.fixture
def evolution_webhook_payload():
    """Payload de teste do webhook."""
    return {
        "event": "messages.upsert",
        "data": {
            "instanceId": "test",
            "messages": [{...}]
        }
    }
```

### Fixtures de Mock

```python
@pytest.fixture
def mock_openai(mocker):
    """Mock da API OpenAI."""
    return mocker.patch("src.services.openai_agent.OpenAI")
```

## 📝 Exemplos de Testes

### Teste Simples (Unit)

```python
# tests/unit/test_validators.py

import pytest
from src.utils.validators import validate_phone

@pytest.mark.unit
class TestValidatePhone:
    """Testa validação de telefone."""

    def test_valid_phone(self):
        assert validate_phone("11999999999") is True
        assert validate_phone("5511999999999") is True

    def test_invalid_phone(self):
        assert validate_phone("123") is False
        assert validate_phone("") is False

    @pytest.mark.parametrize("phone,expected", [
        ("11999999999", True),
        ("invalid", False),
        ("", False),
    ])
    def test_parametrized(self, phone, expected):
        assert validate_phone(phone) == expected
```

### Teste com BD (Integration)

```python
# tests/integration/test_database.py

import pytest
from src.models.lead import Lead, LeadStatus

@pytest.mark.integration
def test_create_lead(db):
    """Testa criação de lead."""
    lead = Lead(
        phone="5511999999999",
        status=LeadStatus.NOVO
    )
    db.add(lead)
    db.commit()

    # Verificar
    retrieved = db.query(Lead).filter_by(phone="5511999999999").first()
    assert retrieved is not None
    assert retrieved.status == LeadStatus.NOVO
```

### Teste de API (E2E)

```python
# tests/e2e/test_webhook.py

import pytest
import json

@pytest.mark.e2e
def test_webhook_flow(client, mock_openai):
    """Testa fluxo completo do webhook."""
    payload = {
        "event": "messages.upsert",
        "data": {
            "instanceId": "test",
            "messages": [{
                "key": {"remoteJid": "5511999999999@s.whatsapp.net", "fromMe": False},
                "message": {"conversation": "Olá, gostaria de abrir franquia"}
            }]
        }
    }

    # Fazer requisição
    response = client.post(
        "/api/webhooks/evolution",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"Authorization": "Bearer test-webhook-secret"}
    )

    # Verificar
    assert response.status_code == 200
    assert response.json["status"] == "ok"
```

## 🔍 Cobertura de Código

### Gerar Relatório

```bash
# Com HTML
pytest --cov=src --cov-report=html

# Abre em src/htmlcov/index.html
open htmlcov/index.html
```

### Requisitos de Cobertura

```bash
# Falha se cobertura < 80%
pytest --cov=src --cov-fail-under=80
```

## 🐛 Debugging de Testes

### Modo Verbose

```bash
# Ver detalhes de cada teste
pytest -v
pytest -vv  # muito verbose
```

### Parar no Erro

```bash
# Parar no primeiro erro
pytest -x

# Parar após N erros
pytest --maxfail=3
```

### Debugar com pdb

```python
def test_algo():
    x = 5
    import pdb; pdb.set_trace()  # Para aqui
    assert x == 10
```

Comandos do pdb:
- `c`: continuar
- `n`: próxima linha
- `s`: step into
- `p x`: print variável

### Mostrar Prints

```bash
# Mostrar output de print() em testes
pytest -s
```

## ⚙️ Configuração (pytest.ini)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
```

## 📊 CI/CD (GitHub Actions)

Testes rodam automaticamente em:
1. **Push em develop**: Todos os testes
2. **Push em main**: Todos os testes
3. **Pull Request**: Testes + linting

Ver `.github/workflows/ci.yml`

## 🚀 Estratégia de Testes

### MVP (v1.0)

```
Unit tests:
✅ Validators
✅ Regional validation
✅ Security functions
✅ Utilities

E2E tests:
✅ Lead reception
✅ Regional validation
✅ Scheduling validation
✅ Rate limiting
✅ Cost tracking

Target: 75% coverage
```

### Fase 2 (v2.0)

```
Integration tests:
- Database operations
- API endpoints
- Follow-up scheduler

Target: 85% coverage
```

### Fase 3 (v3.0)

```
Performance tests:
- Load testing
- Stress testing
- Memory leaks

Target: 90% coverage
```

## 📋 Checklist para Nova Feature

- [ ] Escrever teste primeiro (TDD)
- [ ] Implementar feature
- [ ] Teste passa
- [ ] Coverage >= 80%
- [ ] Testar manualmente
- [ ] Rodar suite completa: `pytest`
- [ ] Criar PR com tests

## 🎯 Exemplos de Cenários

### Cenário 1: Lead Elegível

```python
@pytest.mark.e2e
def test_eligible_lead_workflow(client, db, mock_openai):
    # Setup
    webhook = evolution_webhook_payload()
    webhook['data']['messages'][0]['key']['remoteJid'] = "5551999999999@s.whatsapp.net"
    webhook['data']['messages'][0]['message']['conversation'] = "Quero abrir em RS"

    # Execute
    response = client.post("/api/webhooks/evolution", json=webhook, ...)

    # Assert
    assert response.status_code == 200
    lead = db.query(Lead).first()
    assert lead.regiao == "RS"
    assert lead.elegivel == True
```

### Cenário 2: Validação Regional

```python
@pytest.mark.unit
def test_regional_validation():
    from src.services.regional_validation import RegionalValidator

    validator = RegionalValidator()

    # Elegível
    assert validator.is_eligible("SP") is True
    assert validator.is_eligible("BA") is False  # Nordeste

    # Interesse
    assert validator.is_interest_region("BA") is True
```

## 📚 Referência

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest fixtures](https://docs.pytest.org/fixtures.html)

---

**Precisa de ajuda?** Ver [SETUP.md](./SETUP.md) ou abrir issue
