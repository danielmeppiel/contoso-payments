import datetime
import unittest

from payments.approvals import ApprovalQueue
from payments.ledger import Ledger
from payments.payees import PayeeRegistry
from payments.wires import HOLD_THRESHOLD_CENTS, WireStatus, submit_wire

DAY = datetime.date(2026, 1, 15)


class WireHoldTest(unittest.TestCase):
    def setUp(self):
        self.payees = PayeeRegistry()
        self.payees.register("ACC-001", "Northwind Traders")
        self.approvals = ApprovalQueue()
        self.ledger = Ledger()

    def submit(self, account, payee, amount):
        return submit_wire(
            account,
            payee,
            amount,
            payees=self.payees,
            approvals=self.approvals,
            ledger=self.ledger,
            value_date=DAY,
        )

    def test_threshold_is_integer_cents(self):
        self.assertEqual(HOLD_THRESHOLD_CENTS, 1000000)
        self.assertIsInstance(HOLD_THRESHOLD_CENTS, int)

    def test_just_below_threshold_new_payee_released(self):
        wire = self.submit("ACC-001", "Fabrikam", 999999)
        self.assertIs(wire.status, WireStatus.RELEASED)
        self.assertEqual(self.approvals.pending(), [])
        self.assertEqual(self.ledger.released(), [wire])

    def test_threshold_new_payee_held(self):
        wire = self.submit("ACC-001", "Fabrikam", 1000000)
        self.assertIs(wire.status, WireStatus.HELD)
        self.assertEqual(self.approvals.pending(), [wire])
        self.assertEqual(self.ledger.released(), [])

    def test_above_threshold_new_payee_held(self):
        wire = self.submit("ACC-001", "Fabrikam", 1000001)
        self.assertIs(wire.status, WireStatus.HELD)
        self.assertEqual(len(self.approvals.pending()), 1)

    def test_known_payee_large_amount_released(self):
        wire = self.submit("ACC-001", "Northwind Traders", 5000000)
        self.assertIs(wire.status, WireStatus.RELEASED)
        self.assertEqual(self.approvals.pending(), [])
        self.assertEqual(self.ledger.released(), [wire])

    def test_payee_known_to_other_account_is_new(self):
        wire = self.submit("ACC-002", "Northwind Traders", 1000000)
        self.assertIs(wire.status, WireStatus.HELD)
        self.assertEqual(self.approvals.pending(), [wire])

    def test_small_amount_new_payee_released(self):
        wire = self.submit("ACC-001", "Fabrikam", 1)
        self.assertIs(wire.status, WireStatus.RELEASED)

    def test_submit_does_not_register_payee(self):
        self.submit("ACC-001", "Fabrikam", 1000000)
        self.assertFalse(self.payees.is_known("ACC-001", "Fabrikam"))

    def test_held_wires_have_distinct_ids(self):
        first = self.submit("ACC-001", "Fabrikam", 1000000)
        second = self.submit("ACC-001", "Fabrikam", 1000000)
        self.assertNotEqual(first.wire_id, second.wire_id)
        self.assertEqual(len(self.approvals.pending()), 2)

    def test_invalid_amounts_rejected_before_hold(self):
        cases = [
            (-1, ValueError),
            (0, ValueError),
            (True, TypeError),
            (1000000.0, TypeError),
            ("1000000", TypeError),
        ]
        for amount, error in cases:
            with self.subTest(amount=amount):
                with self.assertRaises(error):
                    self.submit("ACC-001", "Fabrikam", amount)
        self.assertEqual(self.approvals.pending(), [])
        self.assertEqual(self.ledger.released(), [])

    def test_invalid_names_rejected(self):
        cases = [
            (1, "Fabrikam", TypeError),
            ("ACC-001", 1, TypeError),
            (" ", "Fabrikam", ValueError),
            ("ACC-001", "", ValueError),
        ]
        for account, payee, error in cases:
            with self.subTest(account=account, payee=payee):
                with self.assertRaises(error):
                    self.submit(account, payee, 1000000)
        self.assertEqual(self.approvals.pending(), [])
        self.assertEqual(self.ledger.released(), [])

    def test_queue_failure_does_not_record_in_ledger(self):
        class FailingQueue(ApprovalQueue):
            def add(self, payment):
                raise RuntimeError("queue down")

        with self.assertRaises(RuntimeError):
            submit_wire(
                "ACC-001",
                "Fabrikam",
                1000000,
                payees=self.payees,
                approvals=FailingQueue(),
                ledger=self.ledger,
                value_date=DAY,
            )
        self.assertEqual(self.ledger.released(), [])


if __name__ == "__main__":
    unittest.main()
