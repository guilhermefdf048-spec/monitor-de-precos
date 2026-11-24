"""Leitura do arquivo de produtos monitorados."""

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


@dataclass(frozen=True)
class Product:
    name: str
    url: str
    selector: str  # seletor CSS do elemento que mostra o preço
    target_price: Decimal  # avisa quando o preço ficar igual ou abaixo deste valor


def load_products(path: str | Path) -> list[Product]:
    """Carrega a lista de produtos de um arquivo JSON."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    products = []
    for i, item in enumerate(data.get("produtos", []), start=1):
        missing = [k for k in ("nome", "url", "seletor", "preco_alvo") if k not in item]
        if missing:
            raise ValueError(f"produto #{i} sem os campos: {', '.join(missing)}")
        products.append(
            Product(
                name=item["nome"],
                url=item["url"],
                selector=item["seletor"],
                target_price=Decimal(str(item["preco_alvo"])),
            )
        )
    return products
