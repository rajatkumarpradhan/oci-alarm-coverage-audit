import io
import os
import unittest

from alarm_audit import cli

EX = os.path.join(os.path.dirname(__file__), "..", "examples")


class TestCli(unittest.TestCase):
    def test_messy_exit_2(self):
        out = io.StringIO()
        code = cli.run_all(os.path.join(EX, "alarms_messy.json"),
                           os.path.join(EX, "inventory_messy.json"), out=out)
        self.assertEqual(code, 2)
        self.assertIn("audit failed", out.getvalue())

    def test_clean_exit_0(self):
        out = io.StringIO()
        code = cli.run_all(os.path.join(EX, "alarms_clean.json"),
                           os.path.join(EX, "inventory_clean.json"), out=out)
        self.assertEqual(code, 0)
        self.assertIn("clean", out.getvalue())

    def test_error_exit_3(self):
        code = cli.main(["run-all", "/no/such.json",
                         os.path.join(EX, "inventory_messy.json")])
        self.assertEqual(code, 3)

    def test_usage_exit_3(self):
        self.assertEqual(cli.main([]), 3)
        self.assertEqual(cli.main(["bogus", "a", "b"]), 3)


if __name__ == "__main__":
    unittest.main()
