"""Existing wire behaviour that every change must preserve."""

import datetime
import unittest

from payments.approvals import ApprovalQueue
from payments.ledger import Ledger
from payments.payees import PayeeRegistry
from payments.wires import Wire, WireStatus, submit_wire

DAY = datetime.date(2026, 11, 2)


class SubmitWireTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payees = PayeeRegistry(known=(("ACC-001", "Northwind Traders"),))
        self.approvals = ApprovalQueue()
        self.ledger = Ledger()

    def submit(self, account: str, payee: str, amount_cents: object) -> Wire:
        return submit_wire(
            account,
            payee,
            amount_cents,  # type: ignore[arg-type]
            payees=self.payees,
            approvals=self.approvals,
            ledger=self.ledger,
            value_date=DAY,
        )

    def test_small_wire_to_new_payee_is_released(self) -> None:
        wire = self.submit("ACC-001", "Fabrikam", 25_000)
        self.assertIs(wire.status, WireStatus.RELEASED)
        self.assertEqual(wire.amount_cents, 25_000)
        self.assertEqual(wire.value_date, DAY)
        self.assertEqual(self.ledger.released(), [wire])
        self.assertEqual(self.approvals.pending(), [])

    def test_wire_to_known_payee_is_released(self) -> None:
        wire = self.submit("ACC-001", "Northwind Traders", 750_000)
        self.assertIs(wire.status, WireStatus.RELEASED)
        self.assertEqual(self.ledger.released_on("ACC-001", DAY), [wire])

    def test_wire_ids_are_unique(self) -> None:
        first = self.submit("ACC-001", "Fabrikam", 100)
        second = self.submit("ACC-001", "Fabrikam", 100)
        self.assertNotEqual(first.wire_id, second.wire_id)

    def test_wire_is_immutable(self) -> None:
        wire = self.submit("ACC-001", "Fabrikam", 100)
        with self.assertRaises(AttributeError):
            wire.amount_cents = 1  # type: ignore[misc]

    def test_nonpositive_amounts_are_rejected(self) -> None:
        for amount in (0, -1, -1_000_000):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                self.submit("ACC-001", "Fabrikam", amount)
        self.assertEqual(self.ledger.released(), [])

    def test_non_integer_amounts_are_rejected(self) -> None:
        for amount in (True, False, 100.0, "100", None, [100], {"cents": 100}):
            with self.subTest(amount=amount), self.assertRaises(TypeError):
                self.submit("ACC-001", "Fabrikam", amount)
        self.assertEqual(self.ledger.released(), [])

    def test_names_are_validated(self) -> None:
        with self.assertRaises(TypeError):
            submit_wire(None, "Fabrikam", 100, ledger=self.ledger)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            submit_wire("ACC-001", "  ", 100, ledger=self.ledger)
        self.assertEqual(self.ledger.released(), [])


if __name__ == "__main__":
    unittest.main()
