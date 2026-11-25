import os
import unittest

from alarm_audit import model, rules

EX = os.path.join(os.path.dirname(__file__), "..", "examples")


def load_pair(a, i):
    return model.load(os.path.join(EX, a), os.path.join(EX, i))


class TestMessy(unittest.TestCase):
    def setUp(self):
        alarms, resources = load_pair("alarms_messy.json", "inventory_messy.json")
        self.findings = rules.run_all(alarms, resources)

    def test_finds_uncovered_prod_compute(self):
        self.assertTrue(any(f.rule == "ACP001" and "api-2" in f.message
                            for f in self.findings))

    def test_finds_uncovered_prod_db(self):
        self.assertTrue(any(f.rule == "ACP002" and "orders-adb" in f.message
                            for f in self.findings))

    def test_finds_alarm_with_no_destinations(self):
        self.assertTrue(any(f.rule == "ACP003" and "bucket-size-alerts" in f.message
                            for f in self.findings))

    def test_finds_disabled_alarm_covering_prod(self):
        self.assertTrue(any(f.rule == "ACP004" and "prod-mem-db-1" in f.message
                            for f in self.findings))

    def test_finds_uncovered_dev_as_low(self):
        low = [f for f in self.findings if f.rule == "ACP005"]
        self.assertEqual(len(low), 1)
        self.assertEqual(low[0].severity, "LOW")

    def test_terminated_resource_ignored(self):
        self.assertFalse(any("retired-9" in f.message for f in self.findings))

    def test_sorted_high_first(self):
        ranks = [rules.RANK[f.severity] for f in self.findings]
        self.assertEqual(ranks, sorted(ranks))

    def test_high_count(self):
        highs = [f for f in self.findings if f.severity == "HIGH"]
        self.assertEqual(len(highs), 2)


class TestClean(unittest.TestCase):
    def test_clean_pair_has_no_findings(self):
        alarms, resources = load_pair("alarms_clean.json", "inventory_clean.json")
        self.assertEqual(rules.run_all(alarms, resources), [])


if __name__ == "__main__":
    unittest.main()
