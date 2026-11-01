"""Payee registry: which payees each account has already paid."""


def require_name(value: object, field: str) -> str:
    """Return a nonblank account or payee identifier."""
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a string")
    if not value.strip():
        raise ValueError(f"{field} must not be blank")
    return value


class PayeeRegistry:
    """Known payees per account. A payee is new until it is registered."""

    def __init__(self, known: tuple[tuple[str, str], ...] = ()) -> None:
        self._known: set[tuple[str, str]] = set()
        for account, payee in known:
            self.register(account, payee)

    def register(self, account: str, payee: str) -> None:
        """Record that ``account`` has an established relationship with ``payee``."""
        self._known.add((require_name(account, "account"), require_name(payee, "payee")))

    def is_known(self, account: str, payee: str) -> bool:
        """Return True if ``account`` has registered ``payee``."""
        return (require_name(account, "account"), require_name(payee, "payee")) in self._known


REGISTRY = PayeeRegistry()
