"""
Serviço de validação regional.
Define regiões elegíveis e de interesse.
"""
from typing import Tuple, List
from src.config import settings
from src.utils.logging import get_logger


logger = get_logger(__name__)


class RegionalValidator:
    """Validador regional para elegibilidade de franquias."""

    # Mapeamento de estados brasileiros para regiões
    REGIOES_BRASIL = {
        # Sul
        "RS": "sul",
        "SC": "sul",
        "PR": "sul",
        # Sudeste
        "SP": "sudeste",
        "RJ": "sudeste",
        "MG": "sudeste",
        "ES": "sudeste",
        # Centro-Oeste
        "GO": "centro-oeste",
        "MT": "centro-oeste",
        "MS": "centro-oeste",
        "DF": "centro-oeste",
        # Nordeste
        "BA": "nordeste",
        "PE": "nordeste",
        "CE": "nordeste",
        "RN": "nordeste",
        "PB": "nordeste",
        "AL": "nordeste",
        "SE": "nordeste",
        "PI": "nordeste",
        "MA": "nordeste",
        # Norte
        "AP": "norte",
        "AM": "norte",
        "RR": "norte",
        "AC": "norte",
        "TO": "norte",
    }

    def __init__(self):
        """Inicializa validador com regiões do settings."""
        self.eligible_regions = settings.get_eligible_regions()
        self.interest_regions = settings.get_interest_regions()

    def is_eligible(self, region_code: str) -> bool:
        """
        Verifica se região é elegível para franquias.

        Args:
            region_code: Código da região (ex: "SP")

        Returns:
            True se elegível, False caso contrário
        """
        if not region_code:
            return False

        region_upper = region_code.upper()
        return region_upper in [r.upper() for r in self.eligible_regions]

    def is_interest_region(self, region_code: str) -> bool:
        """
        Verifica se região é de interesse (para registro de demanda).

        Args:
            region_code: Código da região

        Returns:
            True se de interesse, False caso contrário
        """
        if not region_code:
            return False

        region_upper = region_code.upper()
        return region_upper in [r.upper() for r in self.interest_regions]

    def get_region_status(self, region_code: str) -> Tuple[str, str]:
        """
        Retorna status da região (elegível, interesse, desconhecida).

        Args:
            region_code: Código da região

        Returns:
            Tuple (status, description)
            - status: "eligible", "interest", "unknown"
            - description: Descrição em português
        """
        if not region_code:
            return "unknown", "Região não informada"

        region_upper = region_code.upper()

        if self.is_eligible(region_code):
            regiao_nome = self.REGIOES_BRASIL.get(region_upper, "desconhecida")
            return "eligible", f"Elegível - Região {regiao_nome.title()}"

        elif self.is_interest_region(region_code):
            regiao_nome = self.REGIOES_BRASIL.get(region_upper, "desconhecida")
            return "interest", f"Região em avaliação - {regiao_nome.title()}"

        else:
            return "unknown", f"Região {region_upper} desconhecida"

    def get_eligible_regions_list(self) -> List[dict]:
        """
        Retorna lista de regiões elegíveis formatada.

        Returns:
            Lista de dicts com código e nome da região
        """
        eligible = []
        for code in self.eligible_regions:
            nome = self.REGIOES_BRASIL.get(code.upper(), code)
            eligible.append({
                "code": code.upper(),
                "name": nome.title(),
                "status": "available"
            })
        return eligible

    def get_interest_regions_list(self) -> List[dict]:
        """
        Retorna lista de regiões de interesse.

        Returns:
            Lista de dicts com código e nome da região
        """
        interest = []
        for code in self.interest_regions:
            nome = self.REGIOES_BRASIL.get(code.upper(), code)
            interest.append({
                "code": code.upper(),
                "name": nome.title(),
                "status": "interest"
            })
        return interest

    def validate_and_log(self, lead_id: str, region_code: str) -> dict:
        """
        Valida região e registra log.

        Args:
            lead_id: ID do lead
            region_code: Código da região

        Returns:
            Dict com resultado da validação
        """
        status, description = self.get_region_status(region_code)
        is_eligible = self.is_eligible(region_code)

        logger.info(
            "region_validated",
            lead_id=lead_id,
            region=region_code,
            status=status,
            is_eligible=is_eligible,
        )

        return {
            "region": region_code.upper() if region_code else None,
            "status": status,
            "is_eligible": is_eligible,
            "description": description,
        }


# Singleton instance
_validator = None


def get_regional_validator() -> RegionalValidator:
    """Retorna instância singleton do validador regional."""
    global _validator
    if _validator is None:
        _validator = RegionalValidator()
    return _validator
