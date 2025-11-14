"""
Model para Scheduling (agendamentos de reuniões).
"""
from datetime import datetime
from enum import Enum
import uuid
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class SchedulingStatus(str, Enum):
    """Estados possíveis de um agendamento."""
    AGENDADO = "agendado"           # Agendamento criado
    CONFIRMADO = "confirmado"       # Lead confirmou presença
    REALIZADO = "realizado"         # Reunião realizada
    CANCELADO = "cancelado"         # Reunião cancelada
    NAO_COMPARECEU = "não_compareceu"  # Lead não compareceu


class Scheduling(Base):
    """
    Tabela de agendamentos/reuniões.
    Um lead pode ter múltiplos agendamentos.
    """
    __tablename__ = "schedulings"

    # ===== Primary Key =====
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # ===== Foreign Key =====
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False, index=True)

    # ===== Reunião =====
    data_reuniao = Column(DateTime, nullable=False, index=True)  # Data/hora da reunião
    status = Column(
        SQLEnum(SchedulingStatus),
        default=SchedulingStatus.AGENDADO,
        nullable=False,
        index=True
    )

    # ===== Vendedor =====
    vendedor_atribuido = Column(String(255), nullable=True)  # Email ou nome do vendedor
    vendedor_email = Column(String(255), nullable=True)      # Email para notificação

    # ===== Observações =====
    notas = Column(String(500), nullable=True)  # Notas da reunião

    # ===== Auditoria =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # ===== Índices =====
    __table_args__ = (
        Index("idx_schedulings_lead_id", "lead_id"),
        Index("idx_schedulings_data_reuniao", "data_reuniao"),
        Index("idx_schedulings_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Scheduling(id={self.id}, lead_id={self.lead_id}, data={self.data_reuniao}, status={self.status})>"

    @property
    def is_upcoming(self) -> bool:
        """Verifica se agendamento é futuro."""
        return self.data_reuniao > datetime.utcnow()

    @property
    def is_past(self) -> bool:
        """Verifica se agendamento é passado."""
        return self.data_reuniao < datetime.utcnow()

    def to_dict(self) -> dict:
        """Converte agendamento para dicionário."""
        return {
            "id": str(self.id),
            "lead_id": str(self.lead_id),
            "data_reuniao": self.data_reuniao.isoformat() if self.data_reuniao else None,
            "status": self.status.value if self.status else None,
            "vendedor_atribuido": self.vendedor_atribuido,
            "vendedor_email": self.vendedor_email,
            "notas": self.notas,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_upcoming": self.is_upcoming,
            "is_past": self.is_past,
        }
