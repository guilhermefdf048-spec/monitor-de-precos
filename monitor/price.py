"""Conversão de textos de preço (ex.: "R$ 1.299,90") para Decimal."""

import re
from decimal import Decimal, InvalidOperation

_NUMBER_RE = re.compile(r"\d[\d.,\s]*")


def parse_price(text: str) -> Decimal:
    """Extrai o primeiro preço de um texto.

    Aceita os formatos brasileiro ("1.299,90") e americano ("1,299.90").
    Lança ValueError se não encontrar um número válido.
    """
    if not text:
        raise ValueError("texto de preço vazio")

    match = _NUMBER_RE.search(text)
    if not match:
        raise ValueError(f"nenhum número encontrado em {text!r}")

    raw = re.sub(r"\s", "", match.group()).strip(".,")

    last_comma = raw.rfind(",")
    last_dot = raw.rfind(".")

    if last_comma > last_dot:
        # Vírgula é o separador decimal: 1.299,90
        normalized = raw.replace(".", "").replace(",", ".")
    elif last_dot > last_comma and last_comma != -1:
        # Ponto é o separador decimal: 1,299.90
        normalized = raw.replace(",", "")
    elif last_dot != -1 and len(raw) - last_dot - 1 == 3:
        # Só pontos com 3 dígitos no final: 1.299 (milhar)
        normalized = raw.replace(".", "")
    else:
        normalized = raw

    try:
        return Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError(f"preço inválido: {text!r}") from exc


def format_brl(value: Decimal) -> str:
    """Formata um valor como moeda brasileira: R$ 1.299,90."""
    formatted = f"{value:,.2f}"  # 1,299.90
    return "R$ " + formatted.replace(",", "X").replace(".", ",").replace("X", ".")
