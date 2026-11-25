"""Interface de linha de comando.

Uso:
    python -m monitor verificar
    python -m monitor loop --intervalo 60
    python -m monitor historico "Nome do produto"
    python -m monitor testar-discord
"""

import argparse
import sys
import time

from .config import ConfigError, load_config
from .monitor import alert_message, check_product
from .notifier import get_webhook, notify, send_discord
from .price import format_brl
from .storage import PriceHistory


def run_once(products_file: str, db_file: str) -> int:
    config = load_config(products_file)
    history = PriceHistory(db_file)
    errors = 0
    try:
        for product in config.products:
            result = check_product(product, history)
            if result.error:
                errors += 1
                print(f"❌ {product.name}: {result.error}")
            elif result.hit_target:
                notify(alert_message(result), config.discord_webhook)
            else:
                print(
                    f"✓ {product.name}: {format_brl(result.price)} "
                    f"(alvo: {format_brl(product.target_price)})"
                )
    finally:
        history.close()
    return 1 if errors == len(config.products) else 0


def show_history(name: str, db_file: str) -> int:
    history = PriceHistory(db_file)
    try:
        rows = history.history(name)
        if not rows:
            print(f"Nenhum registro para {name!r}.")
            return 1
        for when, price in rows:
            print(f"{when}  {format_brl(price)}")
        print(f"\nMenor preço: {format_brl(history.lowest_price(name))}")
    finally:
        history.close()
    return 0


def test_discord(products_file: str) -> int:
    webhook = get_webhook(load_config(products_file).discord_webhook)
    if not webhook:
        print(
            "Nenhum webhook configurado. Coloque em \"discord_webhook\" no "
            f"{products_file} ou na variável DISCORD_WEBHOOK_URL."
        )
        return 1
    if send_discord(webhook, "✅ Monitor de preços conectado! Os alertas vão chegar aqui."):
        print("Mensagem de teste enviada. Confira o canal no Discord.")
        return 0
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="monitor", description="Monitora preços e avisa quando caem."
    )
    parser.add_argument("--produtos", default="produtos.json", help="arquivo de produtos")
    parser.add_argument("--banco", default="historico.db", help="arquivo do histórico")
    sub = parser.add_subparsers(dest="comando", required=True)

    sub.add_parser("verificar", help="verifica todos os produtos uma vez")

    loop = sub.add_parser("loop", help="verifica repetidamente")
    loop.add_argument("--intervalo", type=int, default=60, help="minutos entre verificações")

    hist = sub.add_parser("historico", help="mostra o histórico de um produto")
    hist.add_argument("nome")

    sub.add_parser("testar-discord", help="envia uma mensagem de teste ao Discord")

    args = parser.parse_args(argv)

    try:
        if args.comando == "verificar":
            return run_once(args.produtos, args.banco)

        if args.comando == "loop":
            print(f"Verificando a cada {args.intervalo} min. Ctrl+C para parar.")
            while True:
                run_once(args.produtos, args.banco)
                time.sleep(args.intervalo * 60)

        if args.comando == "testar-discord":
            return test_discord(args.produtos)

        return show_history(args.nome, args.banco)

    except ConfigError as exc:
        print(f"❌ {exc}")
        return 1
    except KeyboardInterrupt:
        print("\nEncerrado.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
