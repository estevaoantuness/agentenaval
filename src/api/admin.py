"""
Rotas administrativas.
Endpoints para monitoramento e controle da aplicação.
"""
from flask import jsonify, g, current_app
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from pydantic import ValidationError

from src.api import admin_bp
from src.config import settings
from src.models.lead import Lead, LeadStatus
from src.models.conversation import Conversation
from src.models.scheduling import Scheduling, SchedulingStatus
from src.schemas.payloads import ErrorResponse
from src.utils.logging import get_logger


logger = get_logger(__name__)


@admin_bp.route("/usage", methods=["GET"])
def get_usage_stats():
    """
    Retorna estatísticas de uso (leads, conversas, custos).

    Returns:
        JSON com estatísticas
    """

    try:
        db = current_app.extensions.get("sqlalchemy")
        if not db:
            return jsonify({"error": "Database not available"}), 500

        # Estatísticas de leads
        total_leads = db.session.query(func.count(Lead.id)).scalar() or 0
        new_leads_24h = db.session.query(func.count(Lead.id)).filter(
            Lead.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).scalar() or 0

        # Estatísticas por status
        status_counts = db.session.query(
            Lead.status,
            func.count(Lead.id)
        ).group_by(Lead.status).all()

        status_breakdown = {
            str(status): count for status, count in status_counts
        }

        # Estatísticas de conversas
        total_conversations = db.session.query(func.count(Conversation.id)).scalar() or 0
        total_tokens = db.session.query(func.sum(Conversation.tokens_total)).scalar() or 0
        total_cost_cents = db.session.query(func.sum(Conversation.custo_estimado)).scalar() or 0
        total_cost_usd = total_cost_cents / 100 if total_cost_cents else 0

        # Estatísticas de agendamentos
        total_schedulings = db.session.query(func.count(Scheduling.id)).scalar() or 0
        scheduled_upcoming = db.session.query(func.count(Scheduling.id)).filter(
            and_(
                Scheduling.status == SchedulingStatus.AGENDADO,
                Scheduling.data_reuniao > datetime.utcnow()
            )
        ).scalar() or 0

        # Latência média
        avg_latency_ms = db.session.query(
            func.avg(Conversation.tempo_resposta_ms)
        ).scalar() or 0

        return jsonify({
            "timestamp": datetime.utcnow().isoformat(),
            "leads": {
                "total": total_leads,
                "new_24h": new_leads_24h,
                "by_status": status_breakdown,
            },
            "conversations": {
                "total": total_conversations,
                "total_tokens": total_tokens,
                "total_cost_usd": round(total_cost_usd, 4),
                "average_latency_ms": round(avg_latency_ms, 2),
            },
            "schedulings": {
                "total": total_schedulings,
                "upcoming": scheduled_upcoming,
            },
            "limits": {
                "cost_limit_monthly": settings.openai_cost_limit_monthly,
                "cost_current": round(total_cost_usd, 4),
                "cost_percentage": round((total_cost_usd / settings.openai_cost_limit_monthly * 100), 1) if settings.openai_cost_limit_monthly else 0,
            },
        }), 200

    except Exception as e:
        logger.error("usage_stats_error", error=str(e), request_id=g.request_id)
        return jsonify(ErrorResponse(
            error="internal_error",
            code=500,
            message="Erro ao buscar estatísticas",
            timestamp=datetime.utcnow(),
            request_id=g.request_id,
        ).model_dump()), 500


@admin_bp.route("/leads", methods=["GET"])
def get_leads():
    """
    Lista todos os leads com filtros opcionais.

    Query params:
    - status: Filtrar por status
    - limit: Número máximo de resultados (padrão 20)
    - offset: Offset para paginação (padrão 0)

    Returns:
        JSON com lista de leads
    """

    try:
        from flask import request

        db = current_app.extensions.get("sqlalchemy")
        if not db:
            return jsonify({"error": "Database not available"}), 500

        # Parâmetros
        status_filter = request.args.get("status")
        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))

        # Query
        query = db.session.query(Lead)

        if status_filter:
            try:
                status_enum = LeadStatus[status_filter.upper()]
                query = query.filter(Lead.status == status_enum)
            except KeyError:
                return jsonify({"error": f"Status inválido: {status_filter}"}), 400

        # Contar total
        total = query.count()

        # Aplicar paginação
        leads = query.order_by(Lead.created_at.desc()).offset(offset).limit(limit).all()

        return jsonify({
            "total": total,
            "limit": limit,
            "offset": offset,
            "leads": [lead.to_dict() for lead in leads],
        }), 200

    except Exception as e:
        logger.error("get_leads_error", error=str(e), request_id=g.request_id)
        return jsonify(ErrorResponse(
            error="internal_error",
            code=500,
            message="Erro ao listar leads",
            timestamp=datetime.utcnow(),
            request_id=g.request_id,
        ).model_dump()), 500


@admin_bp.route("/leads/<lead_id>", methods=["GET"])
def get_lead_detail(lead_id: str):
    """
    Retorna detalhes de um lead específico.

    Args:
        lead_id: ID do lead

    Returns:
        JSON com detalhes do lead
    """

    try:
        db = current_app.extensions.get("sqlalchemy")
        if not db:
            return jsonify({"error": "Database not available"}), 500

        lead = db.session.query(Lead).filter(Lead.id == lead_id).first()

        if not lead:
            return jsonify({"error": "Lead não encontrado"}), 404

        # Conversas
        conversations = db.session.query(Conversation).filter(
            Conversation.lead_id == lead_id
        ).order_by(Conversation.timestamp).all()

        # Agendamentos
        schedulings = db.session.query(Scheduling).filter(
            Scheduling.lead_id == lead_id
        ).order_by(Scheduling.data_reuniao).all()

        return jsonify({
            "lead": lead.to_dict(),
            "conversations": [conv.to_dict() for conv in conversations],
            "schedulings": [sched.to_dict() for sched in schedulings],
        }), 200

    except Exception as e:
        logger.error("get_lead_detail_error", error=str(e), request_id=g.request_id)
        return jsonify(ErrorResponse(
            error="internal_error",
            code=500,
            message="Erro ao buscar detalhes do lead",
            timestamp=datetime.utcnow(),
            request_id=g.request_id,
        ).model_dump()), 500
