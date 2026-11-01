"""Contoso-owned step definitions. They call the real payments interface."""

import datetime
import json
from typing import Any

from behave import given, then, when

VALUE_DATE = datetime.date(2026, 11, 2)


@given('account "{account}" has already paid "{payee}"')
def known_payee(context: Any, account: str, payee: str) -> None:
    context.payees.register(account, payee)


@when('account "{account}" wires {amount:d} cents to "{payee}"')
def wire_cents(context: Any, account: str, amount: int, payee: str) -> None:
    submit(context, account, payee, amount)


@when('account "{account}" submits an amount of {amount} to "{payee}"')
def wire_raw(context: Any, account: str, amount: str, payee: str) -> None:
    submit(context, account, payee, json.loads(amount))


def submit(context: Any, account: str, payee: str, amount: Any) -> None:
    from payments.wires import submit_wire

    try:
        context.wire = submit_wire(
            account,
            payee,
            amount,
            payees=context.payees,
            approvals=context.approvals,
            ledger=context.ledger,
            value_date=VALUE_DATE,
        )
    except (TypeError, ValueError) as exc:
        context.error = exc


@then("the wire is {status:w}")
def wire_status(context: Any, status: str) -> None:
    from payments.wires import WireStatus

    assert context.error is None, f"wire was rejected: {context.error!r}"
    assert context.wire.status is WireStatus[status], context.wire.status
    assert type(context.wire.amount_cents) is int


@then("the wire is rejected with {error:w}")
def wire_rejected(context: Any, error: str) -> None:
    assert context.wire is None, f"wire was accepted: {context.wire!r}"
    assert type(context.error).__name__ == error, repr(context.error)
    assert context.ledger.released() == []


@then("the wire is waiting for approval")
def waiting(context: Any) -> None:
    assert [item.wire_id for item in context.approvals.pending()] == [context.wire.wire_id]


@then("nothing is waiting for approval")
def nothing_waiting(context: Any) -> None:
    assert context.approvals.pending() == []


@then("the wire is not in the ledger")
def not_released(context: Any) -> None:
    assert context.wire.wire_id not in [item.wire_id for item in context.ledger.released()]
