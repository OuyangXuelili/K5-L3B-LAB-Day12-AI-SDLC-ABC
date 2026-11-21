"""Chạy test và sinh bằng chứng thật cho phần Quang; không commit, tag hay gọi API."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def _env():
    return {**os.environ, "PYTHONUTF8": "1",
            "PYTHONPATH": os.pathsep.join((str(ROOT / "tests"), str(ROOT)))}


def run_command(arguments):
    started = time.perf_counter()
    proc = subprocess.run([sys.executable, "-X", "utf8", *arguments], cwd=ROOT,
                          env=_env(), capture_output=True, text=True, encoding="utf-8", timeout=180)
    output = (proc.stdout + proc.stderr).replace(str(ROOT), "<repo>").replace(str(Path.home()), "<user>")
    return {"command": "python " + " ".join(arguments), "exit_code": proc.returncode,
            "duration_seconds": round(time.perf_counter() - started, 3), "output": output}


def _write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def integration_probe():
    """Hái thực, cập bến, đọc kho ở quán; chạy lại để so từng byte."""
    with tempfile.TemporaryDirectory(prefix="phase1-") as temp:
        work = Path(temp)
        scenario, inputs = work / "scenario.json", work / "inputs.json"
        _write(scenario, {"gather": {"player": {"pos": [5, 0]}, "fish": [],
            "nodes": [{"id": "N1", "kind": "bong_sung", "pos": [5, 0]}]}})
        _write(inputs, {"frames": [
            {"tick": 0, "move": [1, 0], "interact": True},
            {"tick": 1, "move": [-1, 0], "interact": False},
            {"tick": 10, "move": [0, 0], "interact": True},
        ]})
        runs = []
        for index in range(2):
            out, inventory = work / f"g{index}.jsonl", work / f"inventory{index}.json"
            result = run_command(["-m", "chonoi.headless", "--mode", "gather", "--seed", "7",
                "--ticks", "20", "--scenario", str(scenario), "--inputs", str(inputs),
                "--out", str(out), "--inventory-out", str(inventory)])
            if result["exit_code"]:
                raise RuntimeError("Gather integration command failed: " + result["output"])
            runs.append((out.read_bytes(), inventory.read_bytes()))
        if runs[0] != runs[1]:
            raise RuntimeError("Same seed/input produced different JSONL or inventory bytes")
        stock = json.loads(runs[0][1])
        if stock != {"items": {"bong_sung": 1}}:
            raise RuntimeError("Unexpected inventory after gathering")
        quan = work / "quan.jsonl"
        result = run_command(["-m", "chonoi.headless", "--mode", "quan", "--seed", "7", "--ticks", "0",
                              "--inventory", str(work / "inventory0.json"), "--out", str(quan)])
        if result["exit_code"]:
            raise RuntimeError("Quan inventory loading failed: " + result["output"])
        rows = [json.loads(line) for line in quan.read_text(encoding="utf-8").splitlines()]
        if rows[0]["stock"] != stock["items"]:
            raise RuntimeError("Quan stock differs from exported gather inventory")
        gathered_rows = [json.loads(line) for line in runs[0][0].decode("utf-8").splitlines()]
        events = [row["name"] for row in gathered_rows if row["type"] == "event"]
        if events != ["gather", "gather_end"]:
            raise RuntimeError("Unexpected gather event order")
        return {"status": "passed", "seed": 7, "events": events, "inventory": stock,
                "quan_stock": rows[0]["stock"], "replay_bytes_identical": True,
                "jsonl_sha256": hashlib.sha256(runs[0][0]).hexdigest(),
                "inventory_sha256": hashlib.sha256(runs[0][1]).hexdigest()}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify Phase 1 starter/gather and write real evidence")
    parser.add_argument("--out", type=Path, default=ROOT / "docs/proof/phase-1/verification.json")
    args = parser.parse_args(argv)
    checks = [run_command(["-m", "unittest", "discover", "-s", "tests", "-v"]),
              run_command(["tools/check_team.py"]),
              run_command(["tools/check_inventory.py"])]
    try:
        probe = integration_probe()
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        probe = {"status": "failed", "error": str(exc).replace(str(ROOT), "<repo>")}
    passed = all(check["exit_code"] == 0 for check in checks) and probe["status"] == "passed"
    report = {"generated_at_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Quang: gather rules, starter regressions, team metadata and inventory integration",
              "status": "passed" if passed else "failed", "checks": checks, "integration": probe,
              "reference": {"title": "PRD-0 — Phase 1 / Test Contract v1.0",
                            "url": "https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-1",
                            "reviewed_sections": ["A", "B", "C", "D (gather)", "E (gather)", "F (Gather)", "G"]},
              "limitations": ["Quan gameplay and final UI remain assigned to other members.",
                              "No human review, phase tag, deadline compliance or team agreement is asserted."]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="\n")
    for check in checks:
        print(f"[{check['exit_code']}] {check['command']}")
    print(f"Integration: {probe['status']}")
    print(f"Verification: {report['status']}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
