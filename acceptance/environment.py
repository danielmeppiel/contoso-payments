"""Fresh, isolated bank state for every acceptance scenario.

Run locally from the repository root: ``PYTHONPATH=src behave acceptance``.
"""

from typing import Any


def before_scenario(context: Any, scenario: Any) -> None:
    from payments.approvals import ApprovalQueue
    from payments.ledger import Ledger
    from payments.payees import PayeeRegistry

    context.payees = PayeeRegistry()
    context.approvals = ApprovalQueue()
    context.ledger = Ledger()
    context.wire = None
    context.error = None
