"""Measure the live gather renderer in Chromium at 1280x720 (requires Playwright)."""
import argparse
import json
import math
from pathlib import Path
import sys
import time

from .contract import load_contract
from .live import LiveGame, LiveServer


def summarize(intervals, measured_s, load_ms):
    if not intervals or measured_s <= 0:
        raise ValueError("No rendered frames were recorded")
    slowest = sorted(intervals, reverse=True)[:max(1, math.ceil(len(intervals) * .01))]
    return {"avg_fps": len(intervals) / measured_s,
            "p1_low_fps": 1000 / (sum(slowest) / len(slowest)),
            "frames": len(intervals), "measured_s": measured_s, "load_ms": load_ms}


def measure(seed, duration):
    from playwright.sync_api import sync_playwright
    tuning = load_contract()["tuning"]
    game = LiveGame("gather", tuning, {}, seed)
    server = LiveServer(game, "127.0.0.1", 0)
    server.start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                started = time.perf_counter()
                page.goto(server.url)
                page.wait_for_function("typeof snap !== 'undefined' && snap && document.querySelector('#c').dataset.fps")
                load_ms = (time.perf_counter() - started) * 1000
                page.set_default_timeout(max(30000, (duration + 10) * 1000))
                sample = page.evaluate("""seconds => new Promise(resolve => {
                    const deltas=[]; let start=null, previous=null;
                    function frame(now) {
                        if(start===null) {start=now;previous=now;}
                        else {deltas.push(now-previous);previous=now;}
                        if(now-start >= seconds*1000) resolve({deltas, elapsed:(now-start)/1000});
                        else requestAnimationFrame(frame);
                    }
                    requestAnimationFrame(frame);
                })""", duration)
                if errors:
                    raise RuntimeError("Renderer error: " + "; ".join(errors))
                state = page.request.get(server.url + "state").json()
                if state.get("error"):
                    raise RuntimeError(state["error"])
                return summarize(sample["deltas"], sample["elapsed"], load_ms)
            finally:
                browser.close()
    finally:
        server.stop()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if not math.isfinite(args.duration) or args.duration <= 0:
        parser.error("--duration must be finite and positive")
    try:
        report = measure(args.seed, args.duration)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except Exception as exc:
        print(f"benchmark failed: {exc}\nInstall: python -m pip install playwright; python -m playwright install chromium", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
