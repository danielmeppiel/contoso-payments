"""Ledger of released outgoing wires."""

import datetime
from typing import Any


class Ledger:
    """Released wires, in release order."""

    def __init__(self) -> None:
        self._entries: list[Any] = []

    def record(self, wire: Any) -> None:
        """Record a released wire."""
        self._entries.append(wire)

    def released(self) -> list[Any]:
        """Return every released wire, oldest first."""
        return list(self._entries)

    def released_on(self, account: str, value_date: datetime.date) -> list[Any]:
        """Return the wires released for ``account`` with ``value_date``."""
        return [
            wire
            for wire in self._entries
            if wire.account == account and wire.value_date == value_date
        ]


LEDGER = Ledger()
