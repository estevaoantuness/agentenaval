"""
Funções de segurança (autenticação, criptografia, validação de webhook).
"""
import hmac
import hashlib
from typing import Optional


def validate_webhook_signature(
    body: str,
    signature: str,
    secret: str,
    algorithm: str = "sha256"
) -> bool:
    """
    Valida assinatura HMAC do webhook.

    Args:
        body: Body da requisição (string)
        signature: Signature recebida no header
        secret: Secret compartilhado
        algorithm: Algoritmo de hash (sha256, sha1, etc)

    Returns:
        True se assinatura é válida, False caso contrário
    """
    try:
        # Calcula HMAC esperada
        expected_signature = hmac.new(
            secret.encode(),
            body.encode(),
            getattr(hashlib, algorithm)
        ).hexdigest()

        # Comparação timing-safe para evitar timing attacks
        return hmac.compare_digest(signature, expected_signature)
    except Exception:
        return False


def hash_password(password: str) -> str:
    """
    Hash de senha com SHA256 (simplificado).
    Em produção, usar bcrypt ou argon2.

    Args:
        password: Senha a ser hasheada

    Returns:
        Hash da senha
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica se senha corresponde ao hash.

    Args:
        password: Senha fornecida
        hashed: Hash armazenado

    Returns:
        True se senha é correta
    """
    return hash_password(password) == hashed


def generate_bearer_token() -> str:
    """
    Gera um token bearer aleatório.

    Returns:
        Token aleatório de 32 caracteres
    """
    import secrets
    return secrets.token_urlsafe(32)


def extract_bearer_token(auth_header: Optional[str]) -> Optional[str]:
    """
    Extrai token do header Authorization.

    Args:
        auth_header: Header Authorization (ex: "Bearer token123")

    Returns:
        Token ou None se não encontrado
    """
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]
