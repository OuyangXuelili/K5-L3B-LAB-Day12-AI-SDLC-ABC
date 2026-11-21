"""Một lệnh cho Phase 2: test, kiểm kho, replay và benchmark thực thi thật."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from verify_phase1 import ROOT, integration_probe, run_command


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def replay_probe():
    tuning = json.loads((ROOT / "game.contract.json").read_text(encoding="utf-8"))["tuning"]
    kinds = ["ca_loc", "bong_sung", "bong_sung"]
    hold = kinds
    expected_stock = {"ca_loc": 1, "bong_sung": 2}
    if "freshness" in tuning:
        fresh = tuning["freshness"]
        decay = Fraction(str(fresh["gather_decay_per_s"])) / tuning["tick_hz"]
        hold = [{"id": f"I{i}", "kind": kind, "fresh": fresh["initial"]}
                for i, kind in enumerate(kinds, 1)]
        expected_stock = [dict(item, fresh=float(item["fresh"] - decay)) for item in hold]
    with tempfile.TemporaryDirectory(prefix="phase2-") as temp:
        work = Path(temp)
        scenario, inputs = work / "scenario.json", work / "inputs.json"
        write(scenario, {"day": {"money": 200, "earned": 200},
            "gather": {"hold": hold, "time_left_ticks": 1},
            "quan": {"time_left_ticks": 1, "random_customers": False}})
        write(inputs, {"frames": [{"tick": 2, "buy": "oxygen", "shop_done": True},
            {"tick": 3, "shop_done": False}, {"tick": 5, "shop_done": True}]})
        outputs = []
        for i in range(2):
            out = work / f"replay-{i}.jsonl"
            result = run_command(["-m", "chonoi.headless", "--mode", "day", "--days", "2", "--seed", "7",
                "--ticks", "10", "--scenario", str(scenario), "--inputs", str(inputs), "--out", str(out), "--snapshot-every", "1"])
            if result["exit_code"]:
                raise RuntimeError(result["output"])
            outputs.append(out.read_bytes())
        if outputs[0] != outputs[1]:
            raise RuntimeError("Replay khác bytes với cùng seed/input")
        rows = [json.loads(line) for line in outputs[0].decode("utf-8").splitlines()]
        snaps = [r for r in rows if r["type"] == "snapshot"]
        events = [r for r in rows if r["type"] == "event"]
        quan = next(r for r in snaps if r["phase"] == "quan")
        next_day = next(r for r in snaps if r["day"] == 2)
        if quan["stock"] != expected_stock or next_day["player"]["oxygen_max_ticks"] != 2700:
            raise RuntimeError("Sai kho chuyển pha hoặc nâng cấp ngày kế")
        end = rows[-1]
        if end["days_completed"] != 2 or end["money"] != 0 or end["earned"] != 200:
            raise RuntimeError("Sai kết quả xuyên ngày")
        return {"status": "passed", "seed": 7, "replay_bytes_identical": True,
            "sha256": hashlib.sha256(outputs[0]).hexdigest(), "quan_stock": quan["stock"],
            "next_day_oxygen_ticks": next_day["player"]["oxygen_max_ticks"], "end": end,
            "events": [{k: r[k] for k in ("tick", "phase", "day", "name")} for r in events]}


def benchmark():
    with tempfile.TemporaryDirectory(prefix="phase2-bench-") as temp:
        out = Path(temp) / "day.jsonl"
        result = run_command(["-m", "chonoi.headless", "--mode", "day", "--days", "1", "--seed", "7",
                              "--ticks", "22200", "--out", str(out)])
        if result["exit_code"]:
            raise RuntimeError(result["output"])
        rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
        if rows[-1]["reason"] != "days_complete" or rows[-1]["sim_tick"] != 22200:
            raise RuntimeError("Ngày mặc định không hoàn tất ở 22200 tick")
        return {"status": "passed" if result["duration_seconds"] <= 20 else "failed",
            "duration_seconds": result["duration_seconds"], "budget_seconds": 20,
            "machine": "local development machine; official grading machine not measured",
            "end": rows[-1], "event_counts": dict(sorted(Counter(r["name"] for r in rows if r["type"] == "event").items()))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "docs/proof/phase-2/verification.json")
    args = parser.parse_args()
    checks = [run_command(["-m", "unittest", "discover", "-s", "tests", "-v"]),
              run_command(["tools/check_team.py"]), run_command(["tools/check_inventory.py"])]
    probes = {}
    for name, probe in (("gather_inventory", integration_probe), ("day_replay", replay_probe), ("headless_benchmark", benchmark)):
        try:
            probes[name] = probe()
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
            probes[name] = {"status": "failed", "error": str(exc)}
    passed = all(c["exit_code"] == 0 for c in checks) and all(p["status"] == "passed" for p in probes.values())
    version = json.loads((ROOT / "game.contract.json").read_text(encoding="utf-8"))["contract_version"]
    report = {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "contract_version": version,
        "status": "passed" if passed else "failed", "checks": checks, "probes": probes,
        "limitations": ["No human review or on-time lab delivery is asserted.",
            "Restaurant v1.0 payload/fixture details still need PO comparison; see ADR 0002.",
            "Browser visual review and 30 FPS measurement require a working browser session."]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    write(args.out, report)
    for c in checks:
        print(f"[{c['exit_code']}] {c['command']}")
    for name, p in probes.items():
        print(name + ": " + p["status"])
    print("Phase 2: " + report["status"])
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
