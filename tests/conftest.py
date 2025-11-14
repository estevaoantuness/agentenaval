"""
Configuração e fixtures compartilhadas para testes.
"""
import pytest
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Carregar .env de teste
load_dotenv(".env.test", override=True)


# Configurar para usar banco de testes
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["OPENAI_API_KEY"] = "sk-test-key"
os.environ["EVOLUTION_API_URL"] = "http://localhost:3333"
os.environ["EVOLUTION_API_KEY"] = "test-key"
os.environ["EVOLUTION_INSTANCE_ID"] = "test-instance"
os.environ["WEBHOOK_SECRET"] = "test-webhook-secret-min-32-chars"
os.environ["SECRET_KEY"] = "test-secret-key"


@pytest.fixture(scope="session")
def app():
    """Cria aplicação Flask para testes."""
    from src.app import create_app

    app, db = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Cria cliente Flask para fazer requisições."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Cria sessão de banco de dados para testes."""
    from src.app import create_app

    _, db = create_app()
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def runner(app):
    """Cria CLI runner para testes de CLI."""
    return app.test_cli_runner()


# Mock para OpenAI
class MockOpenAIResponse:
    """Mock de resposta OpenAI."""

    class Usage:
        def __init__(self):
            self.prompt_tokens = 10
            self.completion_tokens = 20
            self.total_tokens = 30

    class Message:
        def __init__(self, content):
            self.content = content

    class Choice:
        def __init__(self, content):
            self.message = MockOpenAIResponse.Message(content)

    def __init__(self, content):
        self.choices = [MockOpenAIResponse.Choice(content)]
        self.usage = MockOpenAIResponse.Usage()


@pytest.fixture
def mock_openai(mocker):
    """Mock da API OpenAI."""
    def create_mock_response(content):
        return MockOpenAIResponse(content)

    mock = mocker.patch("src.services.openai_agent.OpenAI")
    mock.return_value.chat.completions.create.return_value = create_mock_response(
        "Olá! Como posso ajudar você?"
    )

    return mock


# Fixtures de dados de teste
@pytest.fixture
def lead_data():
    """Dados de teste para lead."""
    return {
        "phone": "5511999999999",
        "nome": "João Silva",
        "email": "joao@example.com",
        "regiao": "SP",
        "cidade": "São Paulo",
        "interesse": "Abrir franquia",
        "disponibilidade": "Sábado à tarde",
    }


@pytest.fixture
def evolution_webhook_payload():
    """Payload de exemplo do webhook Evolution API."""
    return {
        "event": "messages.upsert",
        "data": {
            "instanceId": "test-instance",
            "messages": [
                {
                    "key": {
                        "remoteJid": "5511999999999@s.whatsapp.net",
                        "fromMe": False,
                        "id": "BAE5123456789",
                    },
                    "message": {
                        "conversation": "Olá, tudo bem? Gostaria de saber mais sobre a franquia"
                    },
                    "messageTimestamp": 1699999999,
                }
            ],
        },
    }
