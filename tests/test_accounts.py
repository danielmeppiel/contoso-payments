"""Payee registry, approval queue, ledger and money helpers."""

import datetime
import types
import unittest

from payments.approvals import ApprovalQueue
from payments.ledger import Ledger
from payments.money import format_cents, require_amount_cents
from payments.payees import PayeeRegistry


class PayeeRegistryTests(unittest.TestCase):
    def test_payees_are_new_until_registered(self) -> None:
        registry = PayeeRegistry()
        self.assertFalse(registry.is_known("ACC-001", "Fabrikam"))
        registry.register("ACC-001", "Fabrikam")
        self.assertTrue(registry.is_known("ACC-001", "Fabrikam"))

    def test_payees_are_known_per_account(self) -> None:
        registry = PayeeRegistry(known=(("ACC-001", "Fabrikam"),))
        self.assertFalse(registry.is_known("ACC-002", "Fabrikam"))

    def test_blank_names_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            PayeeRegistry().register("ACC-001", "")


class ApprovalQueueTests(unittest.TestCase):
    def test_queue_keeps_arrival_order_and_removes(self) -> None:
        queue = ApprovalQueue()
        first = types.SimpleNamespace(wire_id="W1")
        second = types.SimpleNamespace(wire_id="W2")
        queue.add(first)
        queue.add(second)
        self.assertEqual(queue.pending(), [first, second])
        self.assertIs(queue.remove("W1"), first)
        self.assertEqual(queue.pending(), [second])

    def test_duplicates_and_unknown_ids_are_rejected(self) -> None:
        queue = ApprovalQueue()
        queue.add(types.SimpleNamespace(wire_id="W1"))
        with self.assertRaises(ValueError):
            queue.add(types.SimpleNamespace(wire_id="W1"))
        with self.assertRaises(KeyError):
            queue.remove("W9")


class LedgerTests(unittest.TestCase):
    def test_released_on_filters_by_account_and_date(self) -> None:
        ledger = Ledger()
        day = datetime.date(2026, 11, 2)
        mine = types.SimpleNamespace(account="ACC-001", value_date=day)
        other = types.SimpleNamespace(account="ACC-002", value_date=day)
        later = types.SimpleNamespace(account="ACC-001", value_date=day + datetime.timedelta(1))
        for wire in (mine, other, later):
            ledger.record(wire)
        self.assertEqual(ledger.released_on("ACC-001", day), [mine])
        self.assertEqual(ledger.released(), [mine, other, later])


class MoneyTests(unittest.TestCase):
    def test_format_cents(self) -> None:
        self.assertEqual(format_cents(1_000_000), "$10,000.00")
        self.assertEqual(format_cents(999_999), "$9,999.99")
        self.assertEqual(format_cents(5), "$0.05")
        self.assertEqual(format_cents(-250), "-$2.50")

    def test_require_amount_cents(self) -> None:
        self.assertEqual(require_amount_cents(1), 1)
        with self.assertRaises(TypeError):
            require_amount_cents(True)
        with self.assertRaises(ValueError):
            require_amount_cents(0)


if __name__ == "__main__":
    unittest.main()
