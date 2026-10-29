# OWASP AppSec Auditor v3.0

Claude skill for evidence-based defensive source-code security reviews. Includes opt-in local scanner runner and offline HTML report generator.

## Install
Upload the ZIP as a custom Claude Skill, or copy this folder into your local Claude skills directory as appropriate to your Claude environment.

## Quick start
```bash
python scripts/audit_runner.py --repo /path/to/authorized/project --out /tmp/appsec-results --tools bandit,gitleaks
python scripts/render_report.py --input examples/sample-findings.json --output /tmp/appsec-demo.html
```

Semgrep with `--config auto` may download rules and is skipped by default unless `--allow-network` is explicitly provided. Local tools must already be installed. No scanning occurred when packaging this skill. Scanner findings require manual triage. Review logs for sensitive data before sharing. Never use against an unauthorized target.
