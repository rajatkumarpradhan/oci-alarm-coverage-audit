import os
import tempfile
import unittest

from alarm_audit import model

EX = os.path.join(os.path.dirname(__file__), "..", "examples")


class TestLoad(unittest.TestCase):
    def _write(self, text):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as fh:
            fh.write(text)
        self.addCleanup(os.unlink, path)
        return path

    def test_load_ok(self):
        alarms, resources = model.load(
            os.path.join(EX, "alarms_messy.json"),
            os.path.join(EX, "inventory_messy.json"))
        self.assertEqual(len(alarms), 4)
        self.assertEqual(len(resources), 6)

    def test_rejects_bad_json(self):
        bad = self._write("{not json")
        with self.assertRaises(model.LoadError):
            model.load(bad, os.path.join(EX, "inventory_messy.json"))

    def test_rejects_missing_file(self):
        with self.assertRaises(model.LoadError):
            model.load("/no/such/file.json",
                       os.path.join(EX, "inventory_messy.json"))

    def test_rejects_missing_field(self):
        bad = self._write('{"alarms": [{"id": "a1"}]}')
        with self.assertRaises(model.LoadError):
            model.load(bad, os.path.join(EX, "inventory_messy.json"))

    def test_rejects_unknown_resource_type(self):
        bad = self._write(
            '{"resources": [{"id": "x", "type": "widget", "name": "x",'
            ' "environment": "dev", "state": "ACTIVE"}]}')
        with self.assertRaises(model.LoadError):
            model.load(os.path.join(EX, "alarms_messy.json"), bad)

    def test_rejects_top_level_list(self):
        bad = self._write('[{"id": "a1"}]')
        with self.assertRaises(model.LoadError):
            model.load(bad, os.path.join(EX, "inventory_messy.json"))

    def test_active_resources_filters_terminated(self):
        _, resources = model.load(os.path.join(EX, "alarms_messy.json"),
                                  os.path.join(EX, "inventory_messy.json"))
        active = model.active_resources(resources)
        self.assertEqual(len(active), 5)
        self.assertNotIn("inst-9", [r["id"] for r in active])

    def test_coverage_map(self):
        alarms, _ = model.load(os.path.join(EX, "alarms_messy.json"),
                               os.path.join(EX, "inventory_messy.json"))
        covers = model.coverage_map(alarms)
        self.assertEqual([a["id"] for a in covers["inst-1"]], ["alarm-1"])


if __name__ == "__main__":
    unittest.main()
