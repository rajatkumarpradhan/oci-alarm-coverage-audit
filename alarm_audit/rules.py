"""Coverage rules over synthetic OCI Monitoring alarm exports."""

RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


class Finding:
    def __init__(self, rule, severity, message):
        self.rule = rule
        self.severity = severity
        self.message = message

    def line(self):
        return "[%-6s] %s %s" % (self.severity, self.rule, self.message)


def check(alarms, resources):
    findings = []
    active = [r for r in resources if r["state"] == "ACTIVE"]
    covers = {}
    for alarm in alarms:
        for rid in alarm["covers"]:
            covers.setdefault(rid, []).append(alarm)

    for res in active:
        covering = [a for a in covers.get(res["id"], []) if a["enabled"]]
        if covering:
            continue
        if res["environment"] == "prod":
            sev = "HIGH"
            rule = "ACP001" if res["type"] == "compute-instance" else "ACP002"
            findings.append(Finding(rule, sev,
                "prod %s %r has no enabled alarm covering it; add a Monitoring alarm"
                % (res["type"], res["name"])))
        else:
            findings.append(Finding("ACP005", "LOW",
                "%s %s %r has no enabled alarm covering it"
                % (res["environment"], res["type"], res["name"])))

    for alarm in alarms:
        if alarm["enabled"] and not alarm["destinations"]:
            findings.append(Finding("ACP003", "MEDIUM",
                "enabled alarm %r has no notification destinations; it fires nowhere"
                % alarm["name"]))
        if not alarm["enabled"]:
            prod_covered = [rid for rid in alarm["covers"]
                            if any(r["id"] == rid and r["environment"] == "prod"
                                   and r["state"] == "ACTIVE" for r in resources)]
            if prod_covered:
                findings.append(Finding("ACP004", "MEDIUM",
                    "alarm %r is disabled but covers %d prod resource(s)"
                    % (alarm["name"], len(prod_covered))))

    return findings


def sort_key(f):
    return (RANK[f.severity], f.rule, f.message)


def run_all(alarms, resources):
    findings = check(alarms, resources)
    findings.sort(key=sort_key)
    return findings
