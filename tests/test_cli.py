import json

import pytest

from monitor import notifier
from monitor.__main__ import main
from monitor.config import ConfigError, load_config


def write_config(path, **extra):
    data = {
        "produtos": [{"nome": "A", "url": "https://x", "seletor": ".p", "preco_alvo": 10}],
        **extra,
    }
    path.write_text(json.dumps(data), encoding="utf-8")


def test_missing_file_shows_friendly_message(tmp_path, capsys):
    (tmp_path / "produtos.example.json").write_text("{}", encoding="utf-8")
    code = main(["--produtos", str(tmp_path / "produtos.json"), "verificar"])
    out = capsys.readouterr().out
    assert code == 1
    assert "não encontrado" in out
    assert "copy produtos.example.json produtos.json" in out
    assert "Traceback" not in out


def test_invalid_json_points_to_line(tmp_path):
    file = tmp_path / "produtos.json"
    file.write_text('{\n  "produtos": [\n    {"nome": "A",}\n  ]\n}', encoding="utf-8")
    with pytest.raises(ConfigError, match="linha 3"):
        load_config(file)


def test_empty_product_list(tmp_path):
    file = tmp_path / "produtos.json"
    file.write_text('{"produtos": []}', encoding="utf-8")
    with pytest.raises(ConfigError, match="Nenhum produto"):
        load_config(file)


def test_webhook_from_file_and_env(tmp_path, monkeypatch):
    file = tmp_path / "produtos.json"
    write_config(file, discord_webhook="https://discord.com/api/webhooks/arquivo")
    webhook = load_config(file).discord_webhook

    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
    assert notifier.get_webhook(webhook).endswith("/arquivo")

    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/env")
    assert notifier.get_webhook(webhook).endswith("/env")


def test_testar_discord_sends_message(tmp_path, monkeypatch, capsys):
    file = tmp_path / "produtos.json"
    write_config(file, discord_webhook="https://discord.com/api/webhooks/teste")
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)

    sent = []
    monkeypatch.setattr(
        "monitor.__main__.send_discord", lambda url, msg: sent.append((url, msg)) or True
    )
    assert main(["--produtos", str(file), "testar-discord"]) == 0
    assert sent[0][0].endswith("/teste")
    assert "conectado" in sent[0][1]


def test_testar_discord_without_webhook(tmp_path, monkeypatch, capsys):
    file = tmp_path / "produtos.json"
    write_config(file)
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
    assert main(["--produtos", str(file), "testar-discord"]) == 1
    assert "Nenhum webhook" in capsys.readouterr().out
