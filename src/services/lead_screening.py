"""
Serviço de triagem e qualificação de leads.
Gerencia o fluxo de triagem, coleta de dados e agendamento.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models.lead import Lead, LeadStatus
from src.models.conversation import Conversation
from src.services.openai_agent import OpenAIAgent
from src.services.regional_validation import RegionalValidator
from src.utils.logging import get_logger, log_lead_status_change
from src.utils.validators import sanitize_text, extrair_telefone_whatsapp


logger = get_logger(__name__)


class LeadScreening:
    """Serviço de triagem inteligente de leads."""

    def __init__(self, db: Session):
        """
        Inicializa serviço de triagem.

        Args:
            db: Sessão SQLAlchemy
        """
        self.db = db
        self.agent = OpenAIAgent()
        self.validator = RegionalValidator()

    def receive_lead_message(
        self,
        remote_jid: str,
        message_text: str,
    ) -> Dict[str, Any]:
        """
        Recebe mensagem de lead e processa.

        Args:
            remote_jid: JID do WhatsApp (ex: "5511999999999@s.whatsapp.net")
            message_text: Texto da mensagem

        Returns:
            Dict com resultado do processamento
        """

        try:
            # Extrai telefone do JID
            phone = extrair_telefone_whatsapp(remote_jid)
            if not phone:
                logger.error("invalid_phone_format", remote_jid=remote_jid)
                return {
                    "success": False,
                    "error": "Formato de telefone inválido",
                }

            # Sanitiza mensagem
            clean_message = sanitize_text(message_text)

            # Encontra ou cria lead
            lead = self.db.query(Lead).filter(Lead.phone == phone).first()

            if not lead:
                # Lead novo
                lead = Lead(
                    phone=phone,
                    status=LeadStatus.NOVO,
                    data_contato=datetime.utcnow(),
                )
                self.db.add(lead)
                self.db.commit()
                logger.info("new_lead_created", phone=phone, lead_id=str(lead.id))

            # Muda para em_triagem se estava novo
            if lead.status == LeadStatus.NOVO:
                old_status = lead.status
                lead.status = LeadStatus.EM_TRIAGEM
                self.db.commit()
                log_lead_status_change(str(lead.id), old_status.value, LeadStatus.EM_TRIAGEM.value)

            # Atualiza data de última interação
            lead.data_ultima_interacao = datetime.utcnow()

            # Constrói histórico de conversa
            conversation_history = self._build_conversation_history(lead.id)

            # Gera resposta do agente
            response_text, metadata = self.agent.generate_response(
                user_message=clean_message,
                conversation_history=conversation_history,
                lead_id=str(lead.id),
            )

            # Salva conversa no banco
            conversation = Conversation(
                lead_id=lead.id,
                mensagem_entrada=clean_message,
                mensagem_saida=response_text,
                tokens_input=metadata.get("tokens_input"),
                tokens_output=metadata.get("tokens_output"),
                tokens_total=metadata.get("tokens_total"),
                custo_estimado=metadata.get("cost_cents"),
                tempo_resposta_ms=metadata.get("latency_ms"),
            )
            self.db.add(conversation)
            self.db.commit()

            # Marca lead para follow-up se não elegível e sem resposta clara
            if lead.status == LeadStatus.AGUARDANDO_RESPOSTA:
                # Se ainda aguardando resposta, marca para follow-up
                lead.mark_for_followup(hours_from_now=2)
                self.db.commit()

            return {
                "success": True,
                "lead_id": str(lead.id),
                "phone": phone,
                "response": response_text,
                "tokens": metadata.get("tokens_total"),
                "latency_ms": metadata.get("latency_ms"),
                "cost_usd": metadata.get("cost_usd"),
            }

        except Exception as e:
            logger.error("lead_screening_error", error=str(e), remote_jid=remote_jid)
            return {
                "success": False,
                "error": str(e),
            }

    def validate_lead_eligibility(self, lead_id: str) -> Dict[str, Any]:
        """
        Valida elegibilidade regional do lead.

        Args:
            lead_id: ID do lead

        Returns:
            Dict com resultado da validação
        """

        try:
            lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                return {"success": False, "error": "Lead não encontrado"}

            if not lead.regiao:
                return {
                    "success": False,
                    "error": "Região não informada",
                }

            # Valida região
            is_eligible, description = self.agent.check_eligibility(
                lead.regiao,
                self.validator.eligible_regions,
            )

            # Atualiza lead
            lead.elegivel = is_eligible

            # Muda status baseado em elegibilidade
            if is_eligible:
                old_status = lead.status
                lead.status = LeadStatus.AGUARDANDO_RESPOSTA
                log_lead_status_change(lead_id, old_status.value, LeadStatus.AGUARDANDO_RESPOSTA.value)
            else:
                old_status = lead.status
                lead.status = LeadStatus.NAO_ELEGIVEL
                log_lead_status_change(lead_id, old_status.value, LeadStatus.NAO_ELEGIVEL.value)

            self.db.commit()

            logger.info(
                "lead_eligibility_checked",
                lead_id=lead_id,
                region=lead.regiao,
                is_eligible=is_eligible,
            )

            return {
                "success": True,
                "lead_id": lead_id,
                "is_eligible": is_eligible,
                "description": description,
            }

        except Exception as e:
            logger.error("eligibility_validation_error", lead_id=lead_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
            }

    def mark_lead_for_response(self, lead_id: str) -> bool:
        """
        Marca lead como aguardando resposta.

        Args:
            lead_id: ID do lead

        Returns:
            True se sucesso
        """
        try:
            lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                return False

            old_status = lead.status
            lead.status = LeadStatus.AGUARDANDO_RESPOSTA
            lead.mark_for_followup(hours_from_now=2)
            self.db.commit()

            log_lead_status_change(lead_id, old_status.value, LeadStatus.AGUARDANDO_RESPOSTA.value)
            return True

        except Exception as e:
            logger.error("mark_for_response_error", lead_id=lead_id, error=str(e))
            return False

    def _build_conversation_history(self, lead_id: str) -> list:
        """
        Constrói histórico de conversa para contexto do agente.

        Args:
            lead_id: ID do lead

        Returns:
            Lista de dicts com role e content para API OpenAI
        """
        try:
            conversations = self.db.query(Conversation).filter(
                Conversation.lead_id == lead_id
            ).order_by(Conversation.timestamp).limit(10).all()

            history = []
            for conv in conversations:
                history.append({
                    "role": "user",
                    "content": conv.mensagem_entrada,
                })
                history.append({
                    "role": "assistant",
                    "content": conv.mensagem_saida,
                })

            return history

        except Exception as e:
            logger.error("build_history_error", lead_id=lead_id, error=str(e))
            return []
