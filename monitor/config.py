"""Leitura do arquivo de configuração (produtos e Discord)."""

import json
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path


class ConfigError(ValueError):
    """Erro no arquivo de configuração, com uma mensagem amigável."""


@dataclass(frozen=True)
class Product:
    name: str
    url: str
    selector: str  # seletor CSS do elemento que mostra o preço
    target_price: Decimal  # avisa quando o preço ficar igual ou abaixo deste valor


@dataclass(frozen=True)
class Config:
    products: list[Product] = field(default_factory=list)
    discord_webhook: str | None = None


def load_config(path: str | Path) -> Config:
    """Carrega produtos e o webhook do Discord de um arquivo JSON."""
    path = Path(path)

    if not path.exists():
        hint = ""
        example = path.with_name("produtos.example.json")
        if example.exists():
            hint = f"\nCrie a partir do modelo:\n    copy {example.name} {path.name}   (Windows)\n    cp {example.name} {path.name}     (Linux/Mac)"
        raise ConfigError(f"Arquivo {path.name!r} não encontrado nesta pasta.{hint}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"Erro no {path.name}, linha {exc.lineno}, coluna {exc.colno}: {exc.msg}.\n"
            "Confira vírgulas, aspas e chaves { }."
        ) from exc

    products = []
    for i, item in enumerate(data.get("produtos", []), start=1):
        missing = [k for k in ("nome", "url", "seletor", "preco_alvo") if k not in item]
        if missing:
            raise ConfigError(f"Produto #{i} no {path.name} sem os campos: {', '.join(missing)}")
        try:
            target = Decimal(str(item["preco_alvo"]))
        except InvalidOperation as exc:
            raise ConfigError(f"Produto #{i}: preco_alvo inválido ({item['preco_alvo']!r})") from exc
        products.append(Product(item["nome"], item["url"], item["seletor"], target))

    if not products:
        raise ConfigError(f"Nenhum produto cadastrado em {path.name}.")

    webhook = (data.get("discord_webhook") or "").strip() or None
    return Config(products=products, discord_webhook=webhook)


def load_products(path: str | Path) -> list[Product]:
    """Atalho que devolve só a lista de produtos."""
    return load_config(path).products
