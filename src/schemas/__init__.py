"""Pydantic schemas para validação."""
from .payloads import (
    EvolutionWebhookPayload,
    LeadSchema,
    ConversationSchema,
    SchedulingSchema,
)

__all__ = [
    "EvolutionWebhookPayload",
    "LeadSchema",
    "ConversationSchema",
    "SchedulingSchema",
]
