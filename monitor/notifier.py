"""Envio de alertas: terminal e, opcionalmente, Discord."""

import os

import requests


def notify(message: str) -> None:
    """Mostra o alerta no terminal e envia ao Discord se configurado.

    Para o Discord, defina a variável de ambiente DISCORD_WEBHOOK_URL
    com a URL de um webhook do seu servidor.
    """
    print(f"🔔 {message}")

    webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    if webhook:
        try:
            requests.post(webhook, json={"content": message}, timeout=10).raise_for_status()
        except requests.RequestException as exc:
            print(f"⚠️  Falha ao enviar para o Discord: {exc}")
