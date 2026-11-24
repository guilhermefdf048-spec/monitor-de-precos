"""Interface de linha de comando.

Uso:
    python -m monitor verificar
    python -m monitor loop --intervalo 60
    python -m monitor historico "Nome do produto"
"""

import argparse
import sys
import time

from .config import load_products
from .monitor import alert_message, check_product
from .notifier import notify
from .price import format_brl
from .storage import PriceHistory


def run_once(products_file: str, db_file: str) -> int:
    products = load_products(products_file)
    history = PriceHistory(db_file)
    errors = 0
    try:
        for product in products:
            result = check_product(product, history)
            if result.error:
                errors += 1
                print(f"❌ {product.name}: {result.error}")
            elif result.hit_target:
                notify(alert_message(result))
            else:
                print(f"✓ {product.name}: {format_brl(result.price)}")
    finally:
        history.close()
    return 1 if errors == len(products) and products else 0


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

    args = parser.parse_args(argv)

    if args.comando == "verificar":
        return run_once(args.produtos, args.banco)

    if args.comando == "loop":
        print(f"Verificando a cada {args.intervalo} min. Ctrl+C para parar.")
        try:
            while True:
                run_once(args.produtos, args.banco)
                time.sleep(args.intervalo * 60)
        except KeyboardInterrupt:
            print("\nEncerrado.")
            return 0

    return show_history(args.nome, args.banco)


if __name__ == "__main__":
    sys.exit(main())
