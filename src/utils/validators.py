"""
Validadores customizados para inputs do sistema.
"""
import re
from typing import List, Optional


def validate_phone(phone: str) -> bool:
    """
    Valida formato de telefone.

    Aceita:
    - Números com 10-15 dígitos
    - Com ou sem código de país
    - Exemplo: 11999999999 ou 5511999999999

    Args:
        phone: Telefone a validar

    Returns:
        True se válido, False caso contrário
    """
    # Remove caracteres especiais
    clean = re.sub(r"\D", "", phone)

    # Valida comprimento
    if len(clean) < 10 or len(clean) > 15:
        return False

    # Verifica se tem pelo menos um dígito que não seja 0
    if all(c == "0" for c in clean):
        return False

    return True


def validate_region(region: str, valid_regions: List[str]) -> bool:
    """
    Valida se região está na lista de regiões válidas.

    Args:
        region: Código de região (ex: "RS", "SP")
        valid_regions: Lista de regiões válidas

    Returns:
        True se válido, False caso contrário
    """
    if not region:
        return False

    region_upper = region.upper()
    return region_upper in [r.upper() for r in valid_regions]


def validate_email(email: str) -> bool:
    """
    Valida formato básico de email.

    Args:
        email: Email a validar

    Returns:
        True se válido, False caso contrário
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_horario(horario: str, inicio: int = 9, fim: int = 18) -> bool:
    """
    Valida formato de horário (HH:MM) e se está em horário comercial.

    Args:
        horario: Horário no formato HH:MM
        inicio: Hora inicial comercial (padrão 9h)
        fim: Hora final comercial (padrão 18h)

    Returns:
        True se válido e em horário comercial
    """
    try:
        pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
        if not re.match(pattern, horario):
            return False

        horas = int(horario.split(":")[0])
        return inicio <= horas < fim

    except (ValueError, IndexError):
        return False


def validate_data_futura(data_str: str, formato: str = "%d/%m/%Y") -> bool:
    """
    Valida se data é futura.

    Args:
        data_str: Data em string (formato padrão: DD/MM/YYYY)
        formato: Formato da data (padrão "%d/%m/%Y")

    Returns:
        True se data é futura, False caso contrário
    """
    from datetime import datetime

    try:
        data = datetime.strptime(data_str, formato)
        return data > datetime.now()
    except ValueError:
        return False


def sanitize_text(text: str, max_length: int = 5000) -> str:
    """
    Sanitiza texto removendo caracteres perigosos.

    Args:
        text: Texto a sanitizar
        max_length: Comprimento máximo

    Returns:
        Texto sanitizado
    """
    if not text:
        return ""

    # Remove caracteres de controle (< 32, exceto \n e \t)
    clean = "".join(c for c in text if ord(c) >= 32 or c in "\n\t")

    # Limita comprimento
    return clean[:max_length]


def extrair_telefone_whatsapp(remote_jid: str) -> Optional[str]:
    """
    Extrai número de telefone do JID do WhatsApp.

    Exemplo: "5511999999999@s.whatsapp.net" → "5511999999999"

    Args:
        remote_jid: JID recebido do Evolution API

    Returns:
        Número de telefone ou None
    """
    if not remote_jid:
        return None

    # Remove @s.whatsapp.net
    phone = remote_jid.split("@")[0]

    if validate_phone(phone):
        return phone

    return None
