#!/usr/bin/env python3
"""Generate a standalone HTML report from manually triaged findings JSON."""
import argparse, html, json
from pathlib import Path

def esc(value): return html.escape(str(value if value is not None else "—"))

def render(data):
    findings = data.get("findings", [])
    counts = {key: sum(f.get("severity") == key for f in findings) for key in ("Critical", "High", "Medium", "Low", "Informational")}
    cards = "".join(f'<div class="stat"><strong>{esc(n)}</strong><span>{esc(k)}</span></div>' for k,n in counts.items())
    rows = "".join('<tr>' + ''.join(f'<td>{esc(f.get(k))}</td>' for k in ("id", "title", "status", "severity", "owasp", "cwe", "location")) + '</tr>' for f in findings)
    details = "".join(f'<section><h3>{esc(f.get("id"))}: {esc(f.get("title"))}</h3><p><b>Evidence:</b> {esc(f.get("evidence"))}</p><p><b>Impact:</b> {esc(f.get("impact"))}</p><p><b>Remediation:</b> {esc(f.get("remediation"))}</p><p><b>Validation:</b> {esc(f.get("validation"))}</p></section>' for f in findings)
    limits = ''.join(f'<li>{esc(x)}</li>' for x in data.get('limitations', []))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>AppSec Audit — {esc(data.get('project'))}</title><style>body{{font:16px system-ui,sans-serif;max-width:1120px;margin:40px auto;padding:0 24px;color:#152338;background:#f7f9fc}}h1{{margin-bottom:4px}}.muted{{color:#5b6777}}.stats{{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}}.stat{{background:white;padding:18px 24px;border:1px solid #dfe5ed;border-radius:12px;min-width:90px}}.stat strong{{display:block;font-size:28px}}.stat span{{font-size:13px}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{text-align:left;padding:11px;border-bottom:1px solid #e4e9ef;vertical-align:top}}.scroll{{overflow:auto}}section{{background:white;border:1px solid #dfe5ed;border-radius:12px;padding:20px;margin:16px 0}}p{{overflow-wrap:anywhere;line-height:1.5}}@media print{{body{{background:white}}section{{break-inside:avoid}}}}</style></head><body><h1>Application Security Audit</h1><p class="muted">Project: {esc(data.get('project'))} · Mode: {esc(data.get('mode'))} · OWASP: {esc(data.get('owasp_edition'))}</p><p><b>Scope:</b> {esc(', '.join(data.get('scope', [])))}</p><div class="stats">{cards}</div><h2>Findings</h2><div class="scroll"><table><thead><tr>{''.join(f'<th>{x}</th>' for x in ('ID','Title','Status','Severity','OWASP','CWE','Location'))}</tr></thead><tbody>{rows}</tbody></table></div><h2>Technical details</h2>{details}<h2>Limitations</h2><ul>{limits}</ul><p class="muted">Scanner alerts require human validation. No security certification is implied.</p></body></html>"""

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--input', required=True); ap.add_argument('--output', required=True); args=ap.parse_args()
    data = json.loads(Path(args.input).read_text(encoding='utf-8'))
    if not isinstance(data.get('findings'), list): ap.error('input must contain findings array')
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True); output.write_text(render(data), encoding='utf-8'); print(output)
if __name__ == '__main__': main()
