"""Testes unitários para validadores."""
import pytest
from src.utils.validators import (
    validate_phone,
    validate_region,
    validate_email,
    validate_horario,
    validate_data_futura,
    sanitize_text,
)


@pytest.mark.unit
class TestValidators:
    """Testes de validadores."""

    def test_validate_phone_valid(self):
        """Testa validação de telefone válido."""
        assert validate_phone("11999999999") is True
        assert validate_phone("5511999999999") is True
        assert validate_phone("11-99999-9999") is True

    def test_validate_phone_invalid(self):
        """Testa validação de telefone inválido."""
        assert validate_phone("123") is False  # Muito curto
        assert validate_phone("") is False  # Vazio
        assert validate_phone("00000000000") is False  # Todos zeros

    def test_validate_email_valid(self):
        """Testa validação de email válido."""
        assert validate_email("user@example.com") is True
        assert validate_email("john.doe@example.co.uk") is True

    def test_validate_email_invalid(self):
        """Testa validação de email inválido."""
        assert validate_email("invalid") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False

    def test_validate_region_valid(self):
        """Testa validação de região válida."""
        regions = ["RS", "SP", "MG"]
        assert validate_region("RS", regions) is True
        assert validate_region("sp", regions) is True  # Case insensitive

    def test_validate_region_invalid(self):
        """Testa validação de região inválida."""
        regions = ["RS", "SP"]
        assert validate_region("BA", regions) is False
        assert validate_region("", regions) is False
        assert validate_region(None, regions) is False

    def test_validate_horario_valid(self):
        """Testa validação de horário válido."""
        assert validate_horario("09:00") is True  # Início comercial
        assert validate_horario("14:30") is True  # Meio do dia
        assert validate_horario("17:59") is True  # Fim comercial

    def test_validate_horario_invalid(self):
        """Testa validação de horário inválido."""
        assert validate_horario("08:00") is False  # Antes do horário comercial
        assert validate_horario("18:00") is False  # Após horário comercial
        assert validate_horario("25:00") is False  # Hora inválida
        assert validate_horario("14:60") is False  # Minuto inválido
        assert validate_horario("invalid") is False

    def test_validate_data_futura_valid(self):
        """Testa validação de data futura."""
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
        assert validate_data_futura(tomorrow) is True

    def test_validate_data_futura_invalid(self):
        """Testa validação de data passada."""
        from datetime import datetime, timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
        assert validate_data_futura(yesterday) is False

    def test_sanitize_text(self):
        """Testa sanitização de texto."""
        # Texto normal
        assert sanitize_text("Hello World") == "Hello World"

        # Com caracteres de controle
        text_with_control = "Hello\x00World"
        result = sanitize_text(text_with_control)
        assert "\x00" not in result

        # Limita comprimento
        long_text = "a" * 10000
        result = sanitize_text(long_text, max_length=100)
        assert len(result) <= 100
