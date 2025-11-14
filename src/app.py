"""
Aplicação Flask principal para automação de WhatsApp.
"""
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import logging
import uuid

from src.config import settings, validate_settings
from src.utils.logging import setup_logging, get_logger
from src.models.lead import Base as LeadBase
from src.models.conversation import Base as ConversationBase
from src.models.scheduling import Base as SchedulingBase
from src.schemas.payloads import HealthCheckResponse, ErrorResponse


logger = get_logger(__name__)


def create_app(config=None) -> Flask:
    """
    Factory para criar aplicação Flask.

    Args:
        config: Configuração customizada (opcional)

    Returns:
        Instância de Flask app
    """

    app = Flask(__name__)

    # ========== Setup Inicial ==========
    try:
        validate_settings()
    except Exception as e:
        logger.error(f"config_validation_failed: {e}")
        raise

    # Setup de logging
    setup_logging(
        log_level=settings.log_level,
        environment=settings.environment,
    )

    # Configuração da app
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_url
    app.config["JSON_SORT_KEYS"] = False

    # ========== CORS ==========
    CORS(
        app,
        origins=settings.cors_origins if isinstance(settings.cors_origins, list) else ["*"],
    )

    # ========== Rate Limiting ==========
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per minute"],
        storage_uri="memory://",
    )

    # ========== Database ==========
    from flask_sqlalchemy import SQLAlchemy

    db = SQLAlchemy(app)

    # Merge bases
    for base in [LeadBase, ConversationBase, SchedulingBase]:
        for table in base.metadata.tables.values():
            table.to_metadata(db.metadata)

    # Cria tabelas se não existirem
    with app.app_context():
        try:
            db.create_all()
            logger.info("database_initialized")
        except Exception as e:
            logger.error(f"database_initialization_failed: {e}")

    # ========== Request/Response Handling ==========

    @app.before_request
    def before_request():
        """Setup antes de cada request."""
        g.request_id = str(uuid.uuid4())
        g.start_time = datetime.utcnow()
        logger.debug(
            "request_start",
            request_id=g.request_id,
            method=request.method,
            path=request.path,
        )

    @app.after_request
    def after_request(response):
        """Cleanup após cada request."""
        if hasattr(g, "start_time"):
            duration_ms = int((datetime.utcnow() - g.start_time).total_seconds() * 1000)
            logger.debug(
                "request_end",
                request_id=g.request_id,
                status=response.status_code,
                duration_ms=duration_ms,
            )
        return response

    @app.errorhandler(404)
    def not_found(error):
        """Handler para 404."""
        return jsonify(ErrorResponse(
            error="not_found",
            code=404,
            message="Endpoint não encontrado",
            timestamp=datetime.utcnow(),
            request_id=g.request_id,
        ).model_dump()), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handler para 500."""
        logger.error("internal_error", error=str(error), request_id=g.request_id)
        return jsonify(ErrorResponse(
            error="internal_error",
            code=500,
            message="Erro interno do servidor",
            timestamp=datetime.utcnow(),
            request_id=g.request_id,
        ).model_dump()), 500

    # ========== Rotas Básicas ==========

    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        try:
            db.session.execute("SELECT 1")
            database_status = "connected"
        except Exception as e:
            logger.error(f"health_check_db_error: {e}")
            database_status = "disconnected"

        response = HealthCheckResponse(
            status="healthy" if database_status == "connected" else "degraded",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            database=database_status,
        )

        return jsonify(response.model_dump()), 200

    @app.route("/status", methods=["GET"])
    @limiter.limit("10 per minute")
    def status():
        """Status da aplicação."""
        return jsonify({
            "status": "operational",
            "environment": settings.environment,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        }), 200

    # ========== API Routes ==========

    from src.api import webhooks_bp, admin_bp

    app.register_blueprint(webhooks_bp, url_prefix="/api/webhooks")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    logger.info("app_initialized", environment=settings.environment)

    return app, db


# Criar app para development/testing
if __name__ == "__main__":
    app, db = create_app()
    app.run(debug=True, port=5000)
