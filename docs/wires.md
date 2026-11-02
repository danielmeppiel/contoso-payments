# Outgoing wires

## How a wire is submitted

[`submit_wire(account, payee, amount_cents)`](../src/payments/wires.py)
validates the request and returns a `Wire` with its `status`. Every amount is
a positive integer number of cents: `1000000` is $10,000.00 (see
[money](../src/payments/money.py)). There is no floating-point money anywhere
in this service.

A valid wire is either `RELEASED` or `HELD` (see
[large wires to new payees](#large-wires-to-new-payees)). A released wire is
recorded in the [ledger](../src/payments/ledger.py).

## Payees

The [payee registry](../src/payments/payees.py) records which payees each
account has already paid. A payee is **new** to an account until it is
registered for that account. Known-ness is per account: a payee that another
account has paid is still new. Submitting a wire does not register the payee.

## Large wires to new payees

A wire of `1000000` cents ($10,000.00) or more to a payee that the sending
account has not paid before is not released. `submit_wire` returns it with
status `WireStatus.HELD` and adds it to the approval queue. A held wire is
not recorded in the ledger. If adding it to the queue fails, the error
propagates and nothing is recorded in the ledger.

The threshold is `HOLD_THRESHOLD_CENTS` in
[the wires module](../src/payments/wires.py).

| Amount (cents) | Payee | Result |
| --- | --- | --- |
| 999999 | new | `RELEASED` |
| 1000000 or more | new | `HELD` |
| any amount | known to the account | `RELEASED` |
| below 1000000 | any | `RELEASED` |

Everything else is unchanged: the signature, the wire id format, the value
date default, and the released path (recorded in the ledger, queue untouched).

## Second approval

The [approval queue](../src/payments/approvals.py) holds payments that wait
for a second person to approve them. Held wires are added to it. Approving or
releasing a held wire is not implemented yet.

## Input errors

| Input | Error |
| --- | --- |
| Amount that is not an `int` (including `True`, `False`, `100.0`, `"100"`) | `TypeError` |
| Amount of zero or less | `ValueError` |
| Account or payee that is not a string | `TypeError` |
| Blank account or payee | `ValueError` |

Validation runs before the hold decision, so a rejected wire is never held
and nothing is queued or recorded.
