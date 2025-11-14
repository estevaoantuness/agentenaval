"""API Routes Blueprints."""
from flask import Blueprint

# Criar blueprints
webhooks_bp = Blueprint("webhooks", __name__)
admin_bp = Blueprint("admin", __name__)

# Importar rotas (isso vai popular os blueprints)
from . import webhooks, admin

__all__ = ["webhooks_bp", "admin_bp"]
