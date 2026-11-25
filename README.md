# oci-alarm-coverage-audit

**Category: custom portfolio tool.** This is NOT an out-of-the-box OCI service
wiring; it is a standalone Python CLI I wrote. Its problem: OCI Monitoring
alarms drift out of sync with the real fleet - instances and databases get
added, alarms get disabled, notification topics get removed - and nobody
notices until an incident has no alarm. This tool audits an alarm export
against a resource inventory and fails the pipeline when coverage gaps exist.

## What it does

- Loads a synthetic Monitoring alarm export (`alarms.json`) and a resource
  inventory (`inventory.json`).
- Maps each ACTIVE resource to the enabled alarms that cover it.
- Applies five rules:

| Rule | Severity | Fires when |
| --- | --- | --- |
| ACP001 | HIGH | a prod compute instance has no enabled alarm covering it |
| ACP002 | HIGH | a prod Autonomous Database has no enabled alarm covering it |
| ACP003 | MEDIUM | an enabled alarm has no notification destinations (fires nowhere) |
| ACP004 | MEDIUM | a disabled alarm still covers prod resources (silent coverage gap) |
| ACP005 | LOW | a dev resource has no enabled alarm covering it |

- Prints findings sorted HIGH first, then a RESULT line.
- Exit codes: `0` clean, `2` findings present, `3` usage/input error - so it
  can gate a CI job.

## What actually ran vs template-only

- Everything in `alarm_audit/` is custom Python (stdlib only, no OCI SDK
  calls) and ran locally and in GitHub Actions CI (see Actions tab).
- The `examples/` JSON files are SYNTHETIC exports in the shape of OCI
  Monitoring / inventory listings. No live OCI tenancy was queried; nothing
  here talks to OCI.
- Simplification to know about: real OCI alarms are MQL query-based and do
  not carry a per-resource `covers` list; these exports pre-resolve that
  mapping. A live version would evaluate MQL or use the Monitoring API.

## Run it

```
python -m alarm_audit run-all examples/alarms_messy.json examples/inventory_messy.json
# -> 5 findings, exit code 2

python -m alarm_audit run-all examples/alarms_clean.json examples/inventory_clean.json
# -> clean, exit code 0
```

## Test it

```
python -m unittest discover -s tests -v
```

21 tests cover loading/validation, all five rules, sort order, terminated
resource handling, and the CLI exit codes. CI runs the tests on Python
3.10/3.11/3.12 plus both demo commands above (messy must exit 2, clean must
exit 0).
