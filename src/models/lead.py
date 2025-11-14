"""
Model para Lead (prospect/cliente em potencial).
"""
from datetime import datetime
from enum import Enum
import uuid
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class LeadStatus(str, Enum):
    """Estados possíveis de um lead."""
    NOVO = "novo"                           # Lead acabou de chegar
    EM_TRIAGEM = "em_triagem"               # Sendo triado pelo agente
    AGUARDANDO_RESPOSTA = "aguardando_resposta"  # Aguardando resposta do lead
    AGENDADO = "agendado"                   # Reunião agendada
    NAO_ELEGIVEL = "não_elegível"           # Região não elegível (mas registramos)
    SEM_RESPOSTA = "sem_resposta"           # Lead não respondeu após SLA
    RECUPERANDO = "recuperando"             # Tentando reengajar
    INATIVO = "inativo"                     # Desistido após 7 dias


class Lead(Base):
    """
    Tabela de leads/prospects.

    Estados: novo → em_triagem → aguardando_resposta → agendado/não_elegível
             sem_resposta → recuperando → inativo
    """
    __tablename__ = "leads"

    # ===== Primary Key =====
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # ===== Contato =====
    phone = Column(String(20), unique=True, nullable=False, index=True)  # Ex: 5511999999999
    nome = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)

    # ===== Localização =====
    regiao = Column(String(2), nullable=True)  # Ex: RS, SP, BA
    cidade = Column(String(100), nullable=True)

    # ===== Qualificação =====
    interesse = Column(String(500), nullable=True)  # Descrição do interesse
    disponibilidade = Column(String(500), nullable=True)  # Horários disponíveis


    # ===== Status =====
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NOVO, nullable=False, index=True)
    elegivel = Column(Boolean, nullable=True)  # True/False/None (ainda não validado)

    # ===== Follow-up =====
    tentativas_follow_up = Column(Integer, default=0, nullable=False)
    data_ultimo_follow_up = Column(DateTime, nullable=True)
    data_proximo_follow_up = Column(DateTime, nullable=True)

    # ===== Agendamento =====
    data_reuniao_preferencial = Column(DateTime, nullable=True)
    horario_preferencial = Column(String(5), nullable=True)  # Ex: 14:30

    # ===== Contato Inicial =====
    data_contato = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    data_ultima_interacao = Column(DateTime, default=datetime.utcnow, nullable=False)

    # ===== Auditoria =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # ===== Índices =====
    __table_args__ = (
        Index("idx_leads_status", "status"),
        Index("idx_leads_regiao", "regiao"),
        Index("idx_leads_elegivel", "elegivel"),
        Index("idx_leads_data_proximo_followup", "data_proximo_follow_up"),
        Index("idx_leads_data_contato", "data_contato"),
    )

    def __repr__(self) -> str:
        return f"<Lead(id={self.id}, phone={self.phone}, nome={self.nome}, status={self.status})>"

    def is_overdue_for_followup(self) -> bool:
        """Verifica se lead está vencido para follow-up."""
        if not self.data_proximo_follow_up:
            return False
        return datetime.utcnow() >= self.data_proximo_follow_up

    def mark_for_followup(self, hours_from_now: int = 2) -> None:
        """Marca lead para follow-up em N horas."""
        from datetime import timedelta
        self.data_proximo_follow_up = datetime.utcnow() + timedelta(hours=hours_from_now)

    def increment_followup_attempts(self) -> None:
        """Incrementa contador de tentativas de follow-up."""
        self.tentativas_follow_up += 1
        self.data_ultimo_follow_up = datetime.utcnow()

    def to_dict(self) -> dict:
        """Converte lead para dicionário."""
        return {
            "id": str(self.id),
            "phone": self.phone,
            "nome": self.nome,
            "email": self.email,
            "regiao": self.regiao,
            "cidade": self.cidade,
            "interesse": self.interesse,
            "disponibilidade": self.disponibilidade,
            "status": self.status.value if self.status else None,
            "elegivel": self.elegivel,
            "tentativas_follow_up": self.tentativas_follow_up,
            "data_ultimo_follow_up": self.data_ultimo_follow_up.isoformat() if self.data_ultimo_follow_up else None,
            "data_proximo_follow_up": self.data_proximo_follow_up.isoformat() if self.data_proximo_follow_up else None,
            "data_reuniao_preferencial": self.data_reuniao_preferencial.isoformat() if self.data_reuniao_preferencial else None,
            "horario_preferencial": self.horario_preferencial,
            "data_contato": self.data_contato.isoformat() if self.data_contato else None,
            "data_ultima_interacao": self.data_ultima_interacao.isoformat() if self.data_ultima_interacao else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
