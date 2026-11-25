"""CLI: audit alarm coverage exports. Exit 0 clean, 2 findings, 3 error."""
import sys

from . import model, rules

USAGE = "usage: python -m alarm_audit run-all ALARMS_JSON INVENTORY_JSON"


def run_all(alarms_path, inventory_path, out=None):
    out = out or sys.stdout
    alarms, resources = model.load(alarms_path, inventory_path)
    findings = rules.run_all(alarms, resources)
    print("Alarm coverage audit - %d alarm(s), %d resource(s)"
          % (len(alarms), len(resources)), file=out)
    for finding in findings:
        print(finding.line(), file=out)
    high = sum(1 for f in findings if f.severity == "HIGH")
    if findings:
        print("RESULT: audit failed - %d HIGH / %d total finding(s) (exit code 2)"
              % (high, len(findings)), file=out)
        return 2
    print("RESULT: coverage audit clean (exit code 0)", file=out)
    return 0


def main(argv):
    if len(argv) == 3 and argv[0] == "run-all":
        try:
            return run_all(argv[1], argv[2])
        except model.LoadError as exc:
            print("error: %s" % exc, file=sys.stderr)
            return 3
    print(USAGE, file=sys.stderr)
    return 3
