"""Envio de alertas: terminal e, opcionalmente, Discord."""

import os

import requests


def get_webhook(config_webhook: str | None = None) -> str | None:
    """A variável de ambiente DISCORD_WEBHOOK_URL tem prioridade sobre o arquivo."""
    return os.environ.get("DISCORD_WEBHOOK_URL") or config_webhook


def send_discord(webhook: str, message: str) -> bool:
    """Envia uma mensagem para um webhook do Discord. Devolve True se deu certo."""
    try:
        requests.post(webhook, json={"content": message}, timeout=10).raise_for_status()
        return True
    except requests.RequestException as exc:
        print(f"⚠️  Falha ao enviar para o Discord: {exc}")
        return False


def notify(message: str, webhook: str | None = None) -> None:
    """Mostra o alerta no terminal e envia ao Discord se houver webhook."""
    print(f"🔔 {message}")
    webhook = get_webhook(webhook)
    if webhook:
        send_discord(webhook, message)
