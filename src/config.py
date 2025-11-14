"""
Configuração centralizada da aplicação.
Carrega e valida variáveis de ambiente.
"""
import os
from typing import List
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import field_validator, HttpUrl


class Settings(BaseSettings):
    """Configurações da aplicação com validação Pydantic."""

    # ========== Database ==========
    database_url: str

    # ========== OpenAI ==========
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 500
    openai_temperature: float = 0.7
    openai_cost_limit_monthly: float = 20.0
    openai_timeout_seconds: int = 3

    # ========== Evolution API ==========
    evolution_api_url: str
    evolution_api_key: str
    evolution_instance_id: str

    # ========== Webhook Security ==========
    webhook_secret: str
    secret_key: str  # Para Flask sessions

    # ========== Prompts ==========
    prompt_version: str = "v1.0"

    # ========== Rate Limiting ==========
    rate_limit_per_phone: int = 30  # req/min
    rate_limit_global: int = 100    # req/min

    # ========== Regiões ==========
    eligible_regions: str = "RS,SC,PR,SP,RJ,MG,ES,GO,MT,MS,DF"
    interest_regions: str = "BA,PE,CE,RN,PB,AL,SE,PI,MA,AP,AM,RR,AC,TO"

    # ========== Email/Notificações ==========
    alert_email: str
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str
    smtp_pass: str
    smtp_from: str

    # ========== Logging ==========
    environment: str = "development"
    log_level: str = "INFO"

    # ========== Scheduling ==========
    scheduler_enabled: bool = False
    scheduler_interval_minutes: int = 30

    # ========== Security ==========
    cors_origins: str = "*"

    # ========== Monitoring ==========
    alert_cost_threshold_warning: float = 0.5    # 50%
    alert_cost_threshold_critical: float = 0.8   # 80%

    # ========== Timeouts ==========
    webhook_timeout_seconds: int = 5
    lead_inactivity_hours: int = 2

    # ========== Feature Flags ==========
    feature_scheduling: bool = True
    feature_notifications: bool = True
    feature_analytics: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False

    @field_validator("eligible_regions", "interest_regions")
    @classmethod
    def parse_regions(cls, v: str) -> List[str]:
        """Converte string comma-separated em lista."""
        return [r.strip() for r in v.split(",") if r.strip()]

    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Converte CORS origins."""
        if v == "*":
            return ["*"]
        return [o.strip() for o in v.split(",") if o.strip()]

    def get_eligible_regions(self) -> List[str]:
        """Retorna lista de regiões elegíveis."""
        if isinstance(self.eligible_regions, str):
            return [r.strip() for r in self.eligible_regions.split(",")]
        return self.eligible_regions

    def get_interest_regions(self) -> List[str]:
        """Retorna lista de regiões de interesse."""
        if isinstance(self.interest_regions, str):
            return [r.strip() for r in self.interest_regions.split(",")]
        return self.interest_regions


@lru_cache()
def get_settings() -> Settings:
    """
    Carrega e cacheia configurações.
    Chamada uma única vez na inicialização.
    """
    return Settings()


def validate_settings() -> Settings:
    """
    Valida todas as configurações necessárias.
    Deve ser chamada na inicialização da app.
    """
    try:
        settings = get_settings()

        # Validações críticas
        required_fields = [
            'database_url',
            'openai_api_key',
            'evolution_api_url',
            'evolution_api_key',
            'evolution_instance_id',
            'webhook_secret',
            'secret_key',
        ]

        for field in required_fields:
            value = getattr(settings, field, None)
            if not value:
                raise ValueError(f"❌ Variável de ambiente obrigatória faltando: {field.upper()}")

        print("✅ Todas as variáveis de ambiente foram validadas com sucesso!")
        return settings

    except Exception as e:
        print(f"❌ Erro ao validar configurações: {e}")
        raise


# Exportar settings singleton
settings = get_settings()
