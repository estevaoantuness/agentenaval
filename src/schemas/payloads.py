"""
Schemas Pydantic para validação de payloads.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator


# ============================================================================
# EVOLUTION API WEBHOOK
# ============================================================================

class EvolutionMessage(BaseModel):
    """Estrutura de mensagem do Evolution API."""
    remoteJid: str  # Ex: 5511999999999@s.whatsapp.net
    fromMe: bool
    id: str
    conversation: Optional[str] = None  # Texto da mensagem


class EvolutionMessageData(BaseModel):
    """Estrutura de dados da mensagem."""
    instanceId: str
    messages: List[EvolutionMessage]


class EvolutionWebhookPayload(BaseModel):
    """Payload completo do webhook Evolution API."""
    event: str  # Ex: "messages.upsert"
    data: EvolutionMessageData


# ============================================================================
# LEAD SCHEMA
# ============================================================================

class LeadSchema(BaseModel):
    """Schema para validação de dados de lead."""
    phone: str = Field(..., min_length=10, max_length=20, description="Telefone com código país")
    nome: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    regiao: Optional[str] = Field(None, max_length=2, description="Código do estado (ex: RS, SP)")
    cidade: Optional[str] = Field(None, max_length=100)
    interesse: Optional[str] = Field(None, max_length=500)
    disponibilidade: Optional[str] = Field(None, max_length=500)

    @validator("phone")
    def validate_phone(cls, v):
        """Valida formato do telefone."""
        # Remove caracteres especiais
        clean = "".join(c for c in v if c.isdigit())
        if len(clean) < 10 or len(clean) > 15:
            raise ValueError("Telefone deve ter entre 10 e 15 dígitos")
        return clean

    @validator("regiao")
    def validate_regiao(cls, v):
        """Valida código de estado."""
        if v and len(v) != 2:
            raise ValueError("Região deve ter 2 caracteres (ex: RS, SP)")
        return v.upper() if v else v

    class Config:
        from_attributes = True


# ============================================================================
# CONVERSATION SCHEMA
# ============================================================================

class ConversationSchema(BaseModel):
    """Schema para validação de conversa."""
    lead_id: str
    mensagem_entrada: str = Field(..., min_length=1, max_length=5000)
    mensagem_saida: str = Field(..., min_length=1, max_length=5000)
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    tokens_total: Optional[int] = None
    custo_estimado: Optional[int] = None  # em centavos
    tempo_resposta_ms: Optional[int] = None

    @validator("mensagem_entrada", "mensagem_saida")
    def sanitize_messages(cls, v):
        """Sanitiza mensagens (remove caracteres perigosos)."""
        # Remove caracteres de controle
        return "".join(c for c in v if ord(c) >= 32 or c in "\n\t")

    class Config:
        from_attributes = True


# ============================================================================
# SCHEDULING SCHEMA
# ============================================================================

class SchedulingSchema(BaseModel):
    """Schema para validação de agendamento."""
    lead_id: str
    data_reuniao: datetime = Field(..., description="Data e hora da reunião")
    horario_preferencial: Optional[str] = Field(None, regex=r"^\d{2}:\d{2}$", description="Formato HH:MM")
    vendedor_atribuido: Optional[str] = Field(None, max_length=255)
    vendedor_email: Optional[EmailStr] = None
    notas: Optional[str] = Field(None, max_length=500)

    @validator("data_reuniao")
    def validate_data_reuniao(cls, v):
        """Valida que data é futura."""
        if v <= datetime.utcnow():
            raise ValueError("Data da reunião deve ser no futuro")
        return v

    @validator("horario_preferencial")
    def validate_horario(cls, v):
        """Valida se horário é comercial (9h-18h)."""
        if v:
            horas = int(v.split(":")[0])
            if horas < 9 or horas > 18:
                raise ValueError("Horário deve ser entre 09:00 e 18:00 (horário comercial)")
        return v

    class Config:
        from_attributes = True


# ============================================================================
# HEALTH CHECK
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Resposta do health check."""
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    version: str
    database: str  # "connected", "disconnected"
    message: Optional[str] = None


# ============================================================================
# ERROR RESPONSE
# ============================================================================

class ErrorResponse(BaseModel):
    """Resposta de erro padrão."""
    error: str
    code: int
    message: str
    timestamp: datetime
    request_id: Optional[str] = None

    class Config:
        from_attributes = True
