"""Generate Phase 4 evidence from real commands; failures remain failures."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/proof/phase-4"


def source_digest():
    digest = hashlib.sha256()
    paths = [ROOT / "game.contract.json"]
    for folder in ("chonoi", "tests", "tools"):
        paths.extend(p for p in (ROOT / folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    for path in sorted(paths):
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def command(args, cwd=ROOT):
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(cwd / "tests"), str(cwd)]), PYTHONIOENCODING="utf-8")
    start = time.perf_counter()
    result = subprocess.run([sys.executable, *args], cwd=cwd, env=env, capture_output=True,
                            encoding="utf-8", errors="replace", timeout=180)
    return {"command": "python " + " ".join(args), "exit_code": result.returncode,
            "duration_s": time.perf_counter()-start, "output": result.stdout + result.stderr}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    checks = []
    jobs = [["-m", "unittest", "discover", "-s", "tests", "-v"],
            ["tools/check_team.py"], ["tools/check_inventory.py"],
            ["-m", "chonoi.soak", "--seed", "7", "--days", "10", "--out", str(OUT / "soak.json")],
            ["-m", "chonoi.soak", "--seed", "7", "--days", "10", "--out", str(OUT / "soak-replay.json")],
            ["-m", "chonoi.bench", "--seed", "42", "--duration", "30", "--out", str(OUT / "bench.json")],
            ["tools/verify_ui.py"], ["tools/package_release.py"]]
    for job in jobs:
        result = command(job)
        checks.append(result)
        print(f"[{result['exit_code']}] {result['command']}", flush=True)
    replay_equal = False
    if all((OUT / n).exists() for n in ("soak.json", "soak-replay.json")):
        reports = [json.loads((OUT / n).read_text()) for n in ("soak.json", "soak-replay.json")]
        for report in reports:
            report.pop("duration_s")
        replay_equal = reports[0] == reports[1]
    # Install nothing: extract the archive and exercise the shipped modules/tests.
    if checks[-1]["exit_code"] == 0:
        with tempfile.TemporaryDirectory(prefix="chonoi-release-") as tmp:
            with zipfile.ZipFile(ROOT / "dist/chonoi-v1.0.0.zip") as archive:
                archive.extractall(tmp)
            clean = Path(tmp) / "chonoi-v1.0.0"
            checks.append(command(["-m", "unittest", "discover", "-s", "tests", "-q"], clean))
            checks.append(command(["-m", "chonoi.soak", "--seed", "7", "--days", "10", "--out", "soak.json"], clean))
            checks.append(command(["-m", "chonoi.headless", "--mode", "day", "--days", "1",
                                   "--seed", "7", "--ticks", "22200", "--out", "day.jsonl"], clean))
    report = {"source_sha256": source_digest(), "contract_version": "1.3",
              "status": "passed" if replay_equal and all(c["exit_code"] == 0 for c in checks) else "failed",
              "soak_gameplay_replay_identical": replay_equal, "checks": checks,
              "limitations": ["Local Windows / Chromium headless; official grading machine not measured.",
                              "Soak idle bot exercises phase deadlines; upgrade/id scenarios are covered by unit tests.",
                              "No human review, historical deadline compliance or published release is asserted."]}
    (OUT / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("Phase 4: " + report["status"])
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
