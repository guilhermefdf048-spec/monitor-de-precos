"""Histórico de preços em SQLite."""

import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT NOT NULL,
    price TEXT NOT NULL,
    checked_at TEXT NOT NULL
)
"""


class PriceHistory:
    def __init__(self, path: str | Path = "historico.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def add(self, product: str, price: Decimal, when: datetime | None = None) -> None:
        when = when or datetime.now()
        self.conn.execute(
            "INSERT INTO prices (product, price, checked_at) VALUES (?, ?, ?)",
            (product, str(price), when.isoformat(timespec="seconds")),
        )
        self.conn.commit()

    def last_price(self, product: str) -> Decimal | None:
        row = self.conn.execute(
            "SELECT price FROM prices WHERE product = ? ORDER BY id DESC LIMIT 1",
            (product,),
        ).fetchone()
        return Decimal(row[0]) if row else None

    def lowest_price(self, product: str) -> Decimal | None:
        rows = self.conn.execute(
            "SELECT price FROM prices WHERE product = ?", (product,)
        ).fetchall()
        return min((Decimal(r[0]) for r in rows), default=None)

    def history(self, product: str) -> list[tuple[str, Decimal]]:
        rows = self.conn.execute(
            "SELECT checked_at, price FROM prices WHERE product = ? ORDER BY id",
            (product,),
        ).fetchall()
        return [(when, Decimal(price)) for when, price in rows]

    def close(self) -> None:
        self.conn.close()
