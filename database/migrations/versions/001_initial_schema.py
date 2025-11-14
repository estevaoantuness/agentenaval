"""Initial schema - Create leads, conversations, and schedulings tables

Revision ID: 001_initial
Revises:
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    op.execute("""
        CREATE TYPE lead_status AS ENUM (
            'novo',
            'em_triagem',
            'aguardando_resposta',
            'agendado',
            'não_elegível',
            'sem_resposta',
            'recuperando',
            'inativo'
        )
    """)

    op.execute("""
        CREATE TYPE scheduling_status AS ENUM (
            'agendado',
            'confirmado',
            'realizado',
            'cancelado',
            'não_compareceu'
        )
    """)

    # Create leads table
    op.create_table(
        'leads',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.func.gen_random_uuid()),
        sa.Column('phone', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('nome', sa.String(255)),
        sa.Column('email', sa.String(255)),
        sa.Column('regiao', sa.String(2), index=True),
        sa.Column('cidade', sa.String(100)),
        sa.Column('interesse', sa.String(500)),
        sa.Column('disponibilidade', sa.String(500)),
        sa.Column('status', sa.Enum('novo', 'em_triagem', 'aguardando_resposta', 'agendado', 'não_elegível', 'sem_resposta', 'recuperando', 'inativo', name='lead_status'), default='novo', nullable=False, index=True),
        sa.Column('elegivel', sa.Boolean),
        sa.Column('tentativas_follow_up', sa.Integer, default=0, nullable=False),
        sa.Column('data_ultimo_follow_up', sa.DateTime),
        sa.Column('data_proximo_follow_up', sa.DateTime, index=True),
        sa.Column('data_reuniao_preferencial', sa.DateTime),
        sa.Column('horario_preferencial', sa.String(5)),
        sa.Column('data_contato', sa.DateTime, nullable=False, server_default=sa.func.now(), index=True),
        sa.Column('data_ultima_interacao', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.func.gen_random_uuid()),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('leads.id'), nullable=False, index=True),
        sa.Column('mensagem_entrada', sa.Text, nullable=False),
        sa.Column('mensagem_saida', sa.Text, nullable=False),
        sa.Column('tokens_input', sa.Integer),
        sa.Column('tokens_output', sa.Integer),
        sa.Column('tokens_total', sa.Integer),
        sa.Column('custo_estimado', sa.Integer),  # em centavos
        sa.Column('tempo_resposta_ms', sa.Integer),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now(), index=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Create schedulings table
    op.create_table(
        'schedulings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.func.gen_random_uuid()),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('leads.id'), nullable=False, index=True),
        sa.Column('data_reuniao', sa.DateTime, nullable=False, index=True),
        sa.Column('status', sa.Enum('agendado', 'confirmado', 'realizado', 'cancelado', 'não_compareceu', name='scheduling_status'), default='agendado', nullable=False, index=True),
        sa.Column('vendedor_atribuido', sa.String(255)),
        sa.Column('vendedor_email', sa.String(255)),
        sa.Column('notas', sa.String(500)),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create indexes
    op.create_index('idx_leads_status', 'leads', ['status'])
    op.create_index('idx_leads_regiao', 'leads', ['regiao'])
    op.create_index('idx_leads_elegivel', 'leads', ['elegivel'])
    op.create_index('idx_leads_data_proximo_followup', 'leads', ['data_proximo_follow_up'])
    op.create_index('idx_leads_data_contato', 'leads', ['data_contato'])
    op.create_index('idx_conversations_lead_id', 'conversations', ['lead_id'])
    op.create_index('idx_conversations_timestamp', 'conversations', ['timestamp'])
    op.create_index('idx_schedulings_lead_id', 'schedulings', ['lead_id'])
    op.create_index('idx_schedulings_data_reuniao', 'schedulings', ['data_reuniao'])
    op.create_index('idx_schedulings_status', 'schedulings', ['status'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('schedulings')
    op.drop_table('conversations')
    op.drop_table('leads')

    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS lead_status")
    op.execute("DROP TYPE IF EXISTS scheduling_status")
