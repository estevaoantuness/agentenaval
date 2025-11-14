"""
WSGI entry point para produção (Gunicorn).
"""
from src.app import create_app


# Criar app - retorna tupla (app, db)
_app, _db = create_app()

# Gunicorn espera um objeto chamado 'app'
app = _app


if __name__ == "__main__":
    app.run()
