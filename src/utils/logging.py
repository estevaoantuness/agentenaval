"""
Setup de logging estruturado com structlog.
"""
import logging
import json
import sys
from datetime import datetime
import structlog
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO", environment: str = "development"):
    """
    Configura logging estruturado com structlog e JSON logging.

    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Ambiente (development, staging, production)
    """

    # Conversão de string para logging level
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Estrutura de logging diferente por ambiente
    if environment == "production":
        # Production: JSON logging para ELK/CloudWatch
        configure_json_logging(level)
    else:
        # Development: Pretty print legível
        configure_dev_logging(level)


def configure_dev_logging(level: int):
    """Configuração para desenvolvimento (pretty print)."""

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Setup handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Formatter simples para development
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

    # Reduzir verbosidade de libraries externas
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def configure_json_logging(level: int):
    """Configuração para produção (JSON logging)."""

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Setup handler com JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # JSON formatter
    formatter = jsonlogger.JsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

    # Reduzir verbosidade de libraries externas
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.typing.FilteringBoundLogger:
    """
    Retorna logger estruturado para um módulo.

    Args:
        name: Nome do módulo (geralmente __name__)

    Returns:
        Logger estruturado
    """
    return structlog.get_logger(name)


# Logger padrão para módulos que não passam name
logger = structlog.get_logger(__name__)


def log_webhook_received(phone: str, event: str, payload_size: int):
    """Log para webhook recebido."""
    get_logger("webhook").info(
        "webhook_received",
        phone=phone,
        event=event,
        payload_size=payload_size,
        timestamp=datetime.utcnow().isoformat(),
    )


def log_openai_call(
    lead_id: str,
    tokens_input: int,
    tokens_output: int,
    cost_usd: float,
    latency_ms: int,
):
    """Log para chamada OpenAI."""
    get_logger("openai").info(
        "openai_call",
        lead_id=lead_id,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        tokens_total=tokens_input + tokens_output,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
        timestamp=datetime.utcnow().isoformat(),
    )


def log_lead_status_change(lead_id: str, old_status: str, new_status: str):
    """Log para mudança de status de lead."""
    get_logger("lead").info(
        "status_change",
        lead_id=lead_id,
        old_status=old_status,
        new_status=new_status,
        timestamp=datetime.utcnow().isoformat(),
    )


def log_error(error_type: str, message: str, details: dict = None):
    """Log para erro."""
    get_logger("error").error(
        error_type,
        message=message,
        details=details or {},
        timestamp=datetime.utcnow().isoformat(),
    )
