"""Outgoing wire transfers."""

import dataclasses
import datetime
import enum
import itertools

from . import approvals as approvals_module
from . import ledger as ledger_module
from . import payees as payees_module
from .money import require_amount_cents
from .payees import require_name

_SEQUENCE = itertools.count(1)

# $10,000.00 in integer cents: wires at or above this to a new payee are held.
HOLD_THRESHOLD_CENTS = 1000000


class WireStatus(enum.Enum):
    """Where a submitted wire stands.

    ``RELEASED`` wires are recorded in the ledger; ``HELD`` wires wait in the
    approval queue for a second approval and are not recorded.
    """

    RELEASED = "released"
    HELD = "held"


@dataclasses.dataclass(frozen=True)
class Wire:
    """A submitted outgoing wire. ``amount_cents`` is a positive integer."""

    wire_id: str
    account: str
    payee: str
    amount_cents: int
    value_date: datetime.date
    status: WireStatus


def submit_wire(
    account: str,
    payee: str,
    amount_cents: int,
    *,
    payees: payees_module.PayeeRegistry | None = None,
    approvals: approvals_module.ApprovalQueue | None = None,
    ledger: ledger_module.Ledger | None = None,
    value_date: datetime.date | None = None,
) -> Wire:
    """Validate and submit an outgoing wire, returning it with its status.

    Invalid input raises before anything is recorded: ``TypeError`` for a
    non-string account or payee, or an amount that is not an ``int`` (``bool``
    included); ``ValueError`` for a blank name or an amount of zero or less.
    A wire of ``HOLD_THRESHOLD_CENTS`` or more to a payee the account has not
    paid before is returned as ``HELD`` and added to the approval queue; it is
    not recorded in the ledger. Other wires are ``RELEASED`` and recorded in
    the ledger.
    """
    require_name(account, "account")
    require_name(payee, "payee")
    require_amount_cents(amount_cents)
    payees = payees_module.REGISTRY if payees is None else payees
    approvals = approvals_module.QUEUE if approvals is None else approvals
    ledger = ledger_module.LEDGER if ledger is None else ledger
    hold = amount_cents >= HOLD_THRESHOLD_CENTS and not payees.is_known(
        account, payee
    )
    wire = Wire(
        wire_id=f"W{next(_SEQUENCE):06d}",
        account=account,
        payee=payee,
        amount_cents=amount_cents,
        value_date=datetime.date.today() if value_date is None else value_date,
        status=WireStatus.HELD if hold else WireStatus.RELEASED,
    )
    if hold:
        approvals.add(wire)
    else:
        ledger.record(wire)
    return wire
