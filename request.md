# Hold large wires to new payees

Hold outgoing wires of $10,000 or more to a new payee for a second approval.

## Rule

- A wire of **$10,000.00 (1000000 cents) or more** to a payee that the sending
  account has **not** paid before (not in its payee registry) is not released.
  `submit_wire` returns it with status `WireStatus.HELD` and adds it to the
  approval queue. A held wire is not recorded in the ledger.
- Wires to known payees are released as before, whatever the amount.
- Wires below $10,000.00 are released as before, whatever the payee.
- A payee is known per account: a payee another account has paid is still new.

## Constraints

- Amounts are integer cents. $10,000.00 is `1000000`; $9,999.99 is `999999`.
- Keep `submit_wire(account, payee, amount_cents, *, payees, approvals, ledger,
  value_date)` and the existing validation: invalid amounts (negative, zero,
  `bool`, non-`int`) are rejected exactly as today, before anything is held or
  recorded.
- Existing behaviour and tests are preserved. Standard library only.

## Definition of done

The scenarios in [`acceptance/wire-hold.feature`](acceptance/wire-hold.feature)
pass. They belong to the bank; the change does not edit them.
