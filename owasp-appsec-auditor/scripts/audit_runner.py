#!/usr/bin/env python3
"""Opt-in offline scanner orchestrator. No package installs or network targets."""
import argparse, datetime, json, os, shutil, subprocess
from pathlib import Path

COMMANDS = {
    "semgrep": lambda repo, out: ["semgrep", "scan", "--config", "auto", "--json", "--output", str(out / "semgrep.json"), "--", str(repo)],
    "bandit": lambda repo, out: ["bandit", "-r", str(repo), "-f", "json", "-o", str(out / "bandit.json")],
    "gitleaks": lambda repo, out: ["gitleaks", "detect", "--source", str(repo), "--no-git", "--report-format", "json", "--report-path", str(out / "gitleaks.json"), "--redact"],
}

def run():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tools", default="semgrep,bandit,gitleaks")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--allow-network", action="store_true", help="Allow tools that fetch rules/updates; off by default")
    args = ap.parse_args()
    repo = Path(args.repo).expanduser().resolve(strict=True)
    if not repo.is_dir(): ap.error("--repo must be a directory")
    out = Path(args.out).expanduser().resolve()
    if out == repo or repo in out.parents: ap.error("--out must be outside repository")
    out.mkdir(parents=True, exist_ok=True)
    selected = [x.strip() for x in args.tools.split(",") if x.strip()]
    if any(x not in COMMANDS for x in selected): ap.error("unknown scanner")
    manifest = {"repo": str(repo), "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "network_allowed": args.allow_network, "scans": []}
    for name in selected:
        exe = shutil.which(name)
        record = {"tool": name, "status": "skipped", "version": None}
        if not exe:
            record["reason"] = "not installed"; manifest["scans"].append(record); continue
        if name == "semgrep" and not args.allow_network:
            record["reason"] = "Semgrep auto rules may access network; provide explicit --allow-network to enable"; manifest["scans"].append(record); continue
        try:
            version = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=10)
            record["version"] = (version.stdout or version.stderr).strip()[:300]
            cmd = COMMANDS[name](repo, out)
            env = dict(os.environ)
            if not args.allow_network: env.update({"PIP_NO_INDEX":"1", "NO_COLOR":"1"})
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout, env=env, cwd=str(out))
            log = out / f"{name}.log"
            log.write_text((proc.stdout + "\n" + proc.stderr)[:2_000_000], encoding="utf-8")
            record.update(status="completed", command=cmd, exit_code=proc.returncode, log=str(log))
        except subprocess.TimeoutExpired:
            record.update(status="timeout", timeout_seconds=args.timeout)
        except OSError as exc:
            record.update(status="error", reason=str(exc))
        manifest["scans"].append(record)
    (out / "scan-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"manifest": str(out / "scan-manifest.json"), "statuses": {x["tool"]: x["status"] for x in manifest["scans"]}}, indent=2))

if __name__ == "__main__": run()
