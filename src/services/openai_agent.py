"""
Serviço de integração com OpenAI.
Gerencia chamadas ao GPT-4o-mini para triagem de leads.
"""
import time
from typing import Optional, Tuple
from datetime import datetime
from openai import OpenAI, APIError, Timeout
from src.config import settings
from src.utils.logging import get_logger


logger = get_logger(__name__)


class OpenAIAgent:
    """Agente inteligente usando OpenAI GPT-4o-mini."""

    def __init__(self):
        """Inicializa cliente OpenAI."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature
        self.timeout = settings.openai_timeout_seconds

    def _load_system_prompt(self, prompt_version: Optional[str] = None) -> str:
        """
        Carrega system prompt do arquivo de versão.

        Args:
            prompt_version: Versão do prompt (ex: v1.0). Se None, usa PROMPT_VERSION da config.

        Returns:
            System prompt
        """
        version = prompt_version or settings.prompt_version

        try:
            prompt_path = f"prompts/{version}/system.txt"
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"prompt_file_not_found", version=version)
            # Fallback para prompt padrão
            return "Você é um assistente útil. Ajude o usuário."

    def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[list] = None,
        lead_id: Optional[str] = None,
        prompt_version: Optional[str] = None,
    ) -> Tuple[str, dict]:
        """
        Gera resposta do agente para mensagem do lead.

        Args:
            user_message: Mensagem do lead
            conversation_history: Histórico de conversa (lista de dicts com 'role' e 'content')
            lead_id: ID do lead (para logging)
            prompt_version: Versão do prompt a usar

        Returns:
            Tuple (resposta, metadata)
            - resposta: Texto da resposta
            - metadata: Dict com tokens, latência, custo, etc
        """

        try:
            # Carrega system prompt
            system_prompt = self._load_system_prompt(prompt_version)

            # Constrói mensagens para API
            messages = [
                {"role": "system", "content": system_prompt},
            ]

            # Adiciona histórico se fornecido
            if conversation_history:
                messages.extend(conversation_history)

            # Adiciona mensagem atual
            messages.append({"role": "user", "content": user_message})

            # Registra início
            start_time = time.time()

            # Chamada à API OpenAI com timeout
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout,
            )

            # Calcula latência
            latency_ms = int((time.time() - start_time) * 1000)

            # Extrai resposta
            assistant_message = response.choices[0].message.content

            # Extrai tokens
            tokens_input = response.usage.prompt_tokens
            tokens_output = response.usage.completion_tokens
            tokens_total = response.usage.total_tokens

            # Calcula custo estimado (em centavos de USD)
            # GPT-4o-mini: $0.00015 por 1K input, $0.0006 por 1K output
            cost_usd = (tokens_input / 1000 * 0.00015) + (tokens_output / 1000 * 0.0006)
            cost_cents = int(cost_usd * 100)

            # Metadata da resposta
            metadata = {
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "tokens_total": tokens_total,
                "cost_usd": cost_usd,
                "cost_cents": cost_cents,
                "latency_ms": latency_ms,
                "model": self.model,
            }

            # Log da chamada
            logger.info(
                "openai_response_generated",
                lead_id=lead_id or "unknown",
                tokens_total=tokens_total,
                latency_ms=latency_ms,
                cost_usd=f"{cost_usd:.6f}",
                timestamp=datetime.utcnow().isoformat(),
            )

            return assistant_message, metadata

        except Timeout:
            logger.error(
                "openai_timeout",
                lead_id=lead_id or "unknown",
                timeout_seconds=self.timeout,
            )
            raise

        except APIError as e:
            logger.error(
                "openai_api_error",
                lead_id=lead_id or "unknown",
                error=str(e),
            )
            raise

        except Exception as e:
            logger.error(
                "openai_unexpected_error",
                lead_id=lead_id or "unknown",
                error=str(e),
            )
            raise

    def check_eligibility(
        self,
        lead_region: str,
        eligible_regions: list,
    ) -> Tuple[bool, str]:
        """
        Verifica elegibilidade regional usando agente.

        Args:
            lead_region: Região do lead (ex: "BA")
            eligible_regions: Lista de regiões elegíveis

        Returns:
            Tuple (is_eligible, explanation)
        """
        region_upper = lead_region.upper() if lead_region else None

        # Verifica se está em regiões elegíveis
        is_eligible = region_upper in [r.upper() for r in eligible_regions]

        if is_eligible:
            explanation = f"Ótimo! A região {lead_region} é elegível para franquias."
        else:
            explanation = (
                f"A região {lead_region} ainda não está aberta para implantações, "
                f"mas vamos registrar seu interesse para futuras expansões."
            )

        return is_eligible, explanation
