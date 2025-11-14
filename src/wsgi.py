"""
WSGI entry point para produção (Gunicorn).
"""
from src.app import create_app


app, db = create_app()


if __name__ == "__main__":
    app.run()
