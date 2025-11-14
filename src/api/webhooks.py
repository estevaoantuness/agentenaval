"""
Rotas de webhook para integração com Evolution API.
"""
from flask import request, jsonify, g, current_app
from datetime import datetime
from pydantic import ValidationError
import hmac
import hashlib

from src.api import webhooks_bp
from src.config import settings
from src.schemas.payloads import EvolutionWebhookPayload, ErrorResponse
from src.services.lead_screening import LeadScreening
from src.utils.logging import get_logger, log_webhook_received
from src.utils.security import extract_bearer_token


logger = get_logger(__name__)


@webhooks_bp.route("/evolution", methods=["POST"])
def evolution_webhook():
    """
    Webhook para receber mensagens da Evolution API.

    Valida assinatura, processa mensagem e retorna resposta.

    Returns:
        JSON response com status
    """

    try:
        # ========== Validação de Segurança ==========

        # Valida Bearer token
        auth_header = request.headers.get("Authorization")
        token = extract_bearer_token(auth_header)

        if not token or token != settings.webhook_secret:
            logger.warning(
                "webhook_authentication_failed",
                request_id=g.request_id,
                ip=request.remote_addr,
            )
            return jsonify(ErrorResponse(
                error="unauthorized",
                code=401,
                message="Token de autenticação inválido",
                timestamp=datetime.utcnow(),
                request_id=g.request_id,
            ).model_dump()), 401

        # ========== Validação de Payload ==========

        try:
            payload_data = request.get_json()
            if not payload_data:
                raise ValueError("Payload vazio")

            payload = EvolutionWebhookPayload(**payload_data)
        except ValidationError as e:
            logger.error(
                "webhook_validation_error",
                request_id=g.request_id,
                error=str(e),
            )
            return jsonify(ErrorResponse(
                error="validation_error",
                code=400,
                message="Payload inválido",
                timestamp=datetime.utcnow(),
                request_id=g.request_id,
            ).model_dump()), 400

        # ========== Processamento da Mensagem ==========

        try:
            # Verifica tipo de evento
            if payload.event != "messages.upsert":
                logger.debug(
                    "webhook_non_message_event",
                    request_id=g.request_id,
                    event=payload.event,
                )
                return jsonify({"status": "ok"}), 200

            # Processa cada mensagem
            for message in payload.data.messages:
                # Ignora mensagens enviadas por nós
                if message.fromMe:
                    continue

                # Extrai dados
                phone = message.remoteJid
                message_text = message.conversation or ""

                # Log de webhook recebido
                log_webhook_received(
                    phone=phone,
                    event=payload.event,
                    payload_size=len(str(payload_data)),
                )

                # Processa com LeadScreening
                db = current_app.extensions.get("sqlalchemy")
                if db:
                    screening = LeadScreening(db.session)
                    result = screening.receive_lead_message(phone, message_text)

                    logger.info(
                        "webhook_message_processed",
                        request_id=g.request_id,
                        phone=phone,
                        success=result.get("success"),
                    )

            return jsonify({"status": "ok"}), 200

        except Exception as e:
            logger.error(
                "webhook_processing_error",
                request_id=g.request_id,
                error=str(e),
            )
            return jsonify(ErrorResponse(
                error="processing_error",
                code=500,
                message="Erro ao processar webhook",
                timestamp=datetime.utcnow(),
                request_id=g.request_id,
            ).model_dump()), 500

    except Exception as e:
        logger.error(
            "webhook_unexpected_error",
            request_id=g.request_id,
            error=str(e),
        )
        return jsonify(ErrorResponse(
            error="unexpected_error",
            code=500,
            message="Erro inesperado ao processar webhook",
            timestamp=datetime.utcnow(),
            request_id=g.request_id,
        ).model_dump()), 500


@webhooks_bp.route("/evolution", methods=["GET"])
def evolution_webhook_verify():
    """
    Verifica webhook (usado por Evolution API na configuração).

    Returns:
        JSON com status de verificação
    """
    logger.info("webhook_verification_request")
    return jsonify({"status": "ok"}), 200
