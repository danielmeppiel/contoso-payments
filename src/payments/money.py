"""Integer-cent amounts: validation and display. Money is never a float."""


def require_amount_cents(amount_cents: object) -> int:
    """Return a positive integer amount, or raise before any comparison.

    ``bool`` is a subclass of ``int`` in Python, so it is rejected explicitly.
    """
    if type(amount_cents) is not int:
        raise TypeError("amount_cents must be an integer number of cents")
    if amount_cents <= 0:
        raise ValueError("amount_cents must be positive")
    return amount_cents


def format_cents(amount_cents: int) -> str:
    """Format integer cents as dollars, for example 1000000 -> '$10,000.00'."""
    if type(amount_cents) is not int:
        raise TypeError("amount_cents must be an integer number of cents")
    sign = "-" if amount_cents < 0 else ""
    dollars, cents = divmod(abs(amount_cents), 100)
    return f"{sign}${dollars:,}.{cents:02d}"
