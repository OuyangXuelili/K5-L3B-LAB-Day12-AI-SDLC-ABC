"""Run consecutive full days through the production simulation, without rendering."""
import argparse
import json
import math
import sys
import time
from pathlib import Path

from .contract import load_contract
from .errors import BadInput
from .inputs import BUTTONS_V11, LiveInputs
from .runner import Session


def run_soak(seed, days):
    tuning = load_contract()["tuning"]
    session = Session("day", tuning, {}, seed, days=days)
    controls = LiveInputs(BUTTONS_V11)
    results = []
    # Idle bot: run every phase to its natural deadline, with no fixture shortcuts.
    budget = days * (sum(round(tuning[p]["duration_s"] * tuning["tick_hz"])
                         for p in ("gather", "quan")) + tuning["shop"]["max_ticks"])
    for _ in range(budget):
        phase = session.sim.phase
        rows = session.step(controls.advance())
        if phase == "shop" and any(r["name"] == "shop_end" for r in rows):
            sim = session.sim
            # A new day's start preserves the balance, earnings and reputation.
            results.append({"day": len(results) + 1, "earned": sim.earned,
                            "reputation": sim.reputation,
                            "score": sim.earned + tuning["score"]["reputation_multiplier"] * math.floor(sim.reputation)})
        if session.done:
            break
    return session.sim.days_completed, results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--days", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.days < 1:
        parser.error("--days must be positive")
    started = time.perf_counter()
    completed, results, crashes = 0, [], 0
    try:
        completed, results = run_soak(args.seed, args.days)
    except BadInput as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:
        crashes = 1
        print(f"soak failed: {exc}", file=sys.stderr)
    report = {"days": args.days, "days_completed": completed, "crashes": crashes,
              "results": results, "duration_s": time.perf_counter() - started}
    try:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0 if not crashes and completed == args.days else 1


if __name__ == "__main__":
    sys.exit(main())
