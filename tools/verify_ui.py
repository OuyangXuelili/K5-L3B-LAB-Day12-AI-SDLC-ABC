"""Exercise warnings and contrast in the real browser using explicit fixtures."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chonoi.contract import load_contract
from chonoi.live import LiveGame, LiveServer


def verify(out):
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    tuning = load_contract()["tuning"]
    fixtures = [
        ("gather", {"player": {"pos": [50, 15], "oxygen_ticks": 200}, "random_fish": False,
                    "monsters": [{"id": "M1", "kind": "ca_sau", "pos": [60, 24],
                                  "waypoints": [[60, 24], [64, 24]]}]},
         [".monster-warning", ".oxygen-warning"]),
        ("quan", {"random_customers": False,
                  "stock": [{"id": "I1", "kind": "ca_loc", "fresh": 100}],
                  "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                                 "patience_ticks_left": 800}]}, [".customer-warning"])]
    checks = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for mode, fixture, selectors in fixtures:
                server = LiveServer(LiveGame(mode, tuning, fixture, 42), "127.0.0.1", 0)
                server.start()
                try:
                    page = browser.new_page(viewport={"width": 1280, "height": 720})
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto(server.url)
                    for selector in selectors:
                        page.locator(selector).wait_for(state="visible")
                    page.locator("#contrast").click()
                    assert page.locator("#contrast").get_attribute("aria-pressed") == "true"
                    for selector in selectors:
                        assert page.locator(selector).is_visible()
                    page.screenshot(path=str(out / f"{mode}-contrast.png"))
                    # Reload retains the setting on the same origin.
                    page.reload()
                    page.wait_for_function("document.body.classList.contains('high-contrast')")
                    for selector in selectors:
                        page.locator(selector).wait_for(state="visible")
                    assert not errors, errors
                    checks.append({"mode": mode, "warnings": selectors, "contrast_persisted": True,
                                   "page_errors": errors, "fixture": fixture})
                    page.close()
                finally:
                    server.stop()
        finally:
            browser.close()
    (out / "ui.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    verify(ROOT / "docs/proof/phase-4")
