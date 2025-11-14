#!/usr/bin/env python3
"""
Script para monitorar uso e custo da OpenAI API.
Executa diariamente e envia alertas se necessário.

Uso:
    python scripts/check_openai_usage.py
"""
import os
import sys
from datetime import datetime, timedelta
import json
from pathlib import Path
import requests
from dotenv import load_dotenv


# Carregar variáveis de ambiente
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_COST_LIMIT_MONTHLY = float(os.getenv("OPENAI_COST_LIMIT_MONTHLY", "20.0"))
ALERT_EMAIL = os.getenv("ALERT_EMAIL")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


def get_openai_usage():
    """
    Consulta API de usage da OpenAI.

    Returns:
        dict com informações de uso
    """
    if not OPENAI_API_KEY:
        print("❌ Variável OPENAI_API_KEY não configurada")
        return None

    try:
        # Calcula data do início do mês
        today = datetime.now()
        start_of_month = today.replace(day=1)

        # Formata datas para query string
        start_date = start_of_month.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

        # Faz request para OpenAI API
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        url = f"https://api.openai.com/v1/usage?start_date={start_date}&end_date={end_date}"

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao consultar OpenAI API: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None


def calculate_cost(usage_data: dict) -> float:
    """
    Calcula custo estimado com base em uso.

    Preços (simplificados):
    - GPT-4o-mini input: $0.00015 por 1K tokens
    - GPT-4o-mini output: $0.0006 por 1K tokens

    Args:
        usage_data: Dados de uso da OpenAI

    Returns:
        Custo em USD
    """
    if not usage_data:
        return 0.0

    # Extrai informações de uso
    total_usage = usage_data.get("data", [])

    total_cost = 0.0

    # Preços do GPT-4o-mini
    gpt4_mini_input_price = 0.00015  # por 1K tokens
    gpt4_mini_output_price = 0.0006  # por 1K tokens

    for day_usage in total_usage:
        # Geralmente a API retorna um objeto por dia
        # Procura por GPT-4o-mini ou modelo similar
        snapshot = day_usage.get("snapshot", {})

        # Calcula custo baseado em tokens
        input_tokens = snapshot.get("gpt-4o-mini", {}).get("input_tokens", 0)
        output_tokens = snapshot.get("gpt-4o-mini", {}).get("output_tokens", 0)

        cost = (input_tokens / 1000 * gpt4_mini_input_price) + \
               (output_tokens / 1000 * gpt4_mini_output_price)
        total_cost += cost

    return total_cost


def send_alert_email(subject: str, message: str):
    """
    Envia email de alerta.

    Args:
        subject: Assunto do email
        message: Corpo da mensagem
    """
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS, ALERT_EMAIL]):
        print("⚠️  Alertas por email não configurados. Pulando envio.")
        return

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # Cria mensagem
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = ALERT_EMAIL
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        # Conecta e envia
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print(f"✅ Email de alerta enviado para {ALERT_EMAIL}")

    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")


def check_usage():
    """
    Verifica uso da OpenAI e gera alertas se necessário.
    """
    print("🔍 Verificando uso da OpenAI API...")

    # Obtém dados de uso
    usage_data = get_openai_usage()

    if not usage_data:
        print("❌ Não foi possível obter dados de uso")
        return

    # Calcula custo
    current_cost = calculate_cost(usage_data)

    # Percentual do limite
    percentage = (current_cost / OPENAI_COST_LIMIT_MONTHLY) * 100

    print(f"\n📊 Custo OpenAI (mês atual):")
    print(f"   Limite: ${OPENAI_COST_LIMIT_MONTHLY:.2f}")
    print(f"   Custo atual: ${current_cost:.2f}")
    print(f"   Percentual: {percentage:.1f}%")

    # Alertas
    if percentage >= 100:
        message = (
            f"⚠️  CRÍTICO: Limite de custo OpenAI atingido!\n\n"
            f"Limite: ${OPENAI_COST_LIMIT_MONTHLY:.2f}\n"
            f"Custo atual: ${current_cost:.2f}\n"
            f"Percentual: {percentage:.1f}%\n\n"
            f"A aplicação será pausada até o mês que vem."
        )
        print(f"🚨 {message}")
        send_alert_email("⚠️ OpenAI - Limite atingido", message)

    elif percentage >= 80:
        message = (
            f"⚠️  AVISO: Você atingiu 80% do limite de custo!\n\n"
            f"Limite: ${OPENAI_COST_LIMIT_MONTHLY:.2f}\n"
            f"Custo atual: ${current_cost:.2f}\n"
            f"Percentual: {percentage:.1f}%\n\n"
            f"Reduza o uso ou aumente o limite para evitar pausas."
        )
        print(f"🔴 {message}")
        send_alert_email("⚠️ OpenAI - 80% do limite", message)

    elif percentage >= 50:
        message = (
            f"ℹ️  Você atingiu 50% do limite de custo.\n\n"
            f"Limite: ${OPENAI_COST_LIMIT_MONTHLY:.2f}\n"
            f"Custo atual: ${current_cost:.2f}\n"
            f"Percentual: {percentage:.1f}%\n\n"
            f"Monitor seu uso regularmente."
        )
        print(f"🟡 {message}")
        send_alert_email("ℹ️ OpenAI - 50% do limite", message)

    else:
        print(f"✅ Dentro do limite. Continuar monitorando.")

    # Salva log localmente
    log_file = Path("logs/openai_usage.json")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "cost": current_cost,
        "limit": OPENAI_COST_LIMIT_MONTHLY,
        "percentage": percentage,
    }

    # Append ao arquivo de log
    try:
        if log_file.exists():
            with open(log_file, "r") as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_entry)

        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)

        print(f"✅ Log salvo em {log_file}")

    except Exception as e:
        print(f"⚠️  Erro ao salvar log: {e}")

    return current_cost


if __name__ == "__main__":
    try:
        cost = check_usage()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)
