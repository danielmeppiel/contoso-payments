"""Second-approval queue for outgoing payments.

A minimal in-memory stub: payments placed here wait for a second person to
approve them. No payment flow uses it yet.
"""

from typing import Any


class ApprovalQueue:
    """Payments waiting for a second approval, in arrival order."""

    def __init__(self) -> None:
        self._pending: dict[str, Any] = {}

    def add(self, payment: Any) -> None:
        """Queue a payment that has a unique ``wire_id``."""
        if payment.wire_id in self._pending:
            raise ValueError(f"{payment.wire_id} is already waiting for approval")
        self._pending[payment.wire_id] = payment

    def pending(self) -> list[Any]:
        """Return the payments waiting for approval, oldest first."""
        return list(self._pending.values())

    def remove(self, wire_id: str) -> Any:
        """Take a payment out of the queue, for example once it is approved."""
        try:
            return self._pending.pop(wire_id)
        except KeyError:
            raise KeyError(f"{wire_id} is not waiting for approval") from None


QUEUE = ApprovalQueue()
