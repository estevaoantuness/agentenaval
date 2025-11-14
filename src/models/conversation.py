"""
Model para Conversation (histórico de conversas com agente).
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Conversation(Base):
    """
    Tabela de conversas entre lead e agente.
    Mantém histórico completo para auditoria e análise.
    """
    __tablename__ = "conversations"

    # ===== Primary Key =====
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # ===== Foreign Key =====
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False, index=True)

    # ===== Mensagens =====
    mensagem_entrada = Column(Text, nullable=False)  # Mensagem do lead
    mensagem_saida = Column(Text, nullable=False)    # Resposta do agente

    # ===== Métricas OpenAI =====
    tokens_input = Column(Integer, nullable=True)      # Tokens da entrada
    tokens_output = Column(Integer, nullable=True)     # Tokens da saída
    tokens_total = Column(Integer, nullable=True)      # Total (input + output)
    custo_estimado = Column(Integer, nullable=True)    # Custo em centavos de dólar

    # ===== Latência =====
    tempo_resposta_ms = Column(Integer, nullable=True)  # Tempo de resposta em milissegundos

    # ===== Auditoria =====
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # ===== Índices =====
    __table_args__ = (
        Index("idx_conversations_lead_id", "lead_id"),
        Index("idx_conversations_timestamp", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, lead_id={self.lead_id}, tokens={self.tokens_total})>"

    def to_dict(self) -> dict:
        """Converte conversa para dicionário."""
        return {
            "id": str(self.id),
            "lead_id": str(self.lead_id),
            "mensagem_entrada": self.mensagem_entrada,
            "mensagem_saida": self.mensagem_saida,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "tokens_total": self.tokens_total,
            "custo_estimado": self.custo_estimado,
            "tempo_resposta_ms": self.tempo_resposta_ms,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
