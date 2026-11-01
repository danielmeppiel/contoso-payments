# Outgoing wires

## How a wire is submitted

[`submit_wire(account, payee, amount_cents)`](../src/payments/wires.py)
validates the request and returns a `Wire` with its `status`. Every amount is
a positive integer number of cents: `1000000` is $10,000.00 (see
[money](../src/payments/money.py)). There is no floating-point money anywhere
in this service.

Today every valid wire is `RELEASED` immediately and recorded in the
[ledger](../src/payments/ledger.py).

## Payees

The [payee registry](../src/payments/payees.py) records which payees each
account has already paid. A payee is **new** to an account until it is
registered for that account.

## Second approval

The [approval queue](../src/payments/approvals.py) holds payments that wait
for a second person to approve them. No wire flow uses it yet.

## Input errors

| Input | Error |
| --- | --- |
| Amount that is not an `int` (including `True`, `False`, `100.0`, `"100"`) | `TypeError` |
| Amount of zero or less | `ValueError` |
| Account or payee that is not a string | `TypeError` |
| Blank account or payee | `ValueError` |

Nothing is recorded when a wire is rejected.
