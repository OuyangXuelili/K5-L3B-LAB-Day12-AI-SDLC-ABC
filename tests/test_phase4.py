"""Phase 4 regression: manifest, inventory compatibility and extended day lifecycle."""
import copy
import tempfile
import unittest
from pathlib import Path

from chonoi.bench import summarize
from chonoi.contract import load_contract
from chonoi.inputs import BUTTONS_V11, LiveInputs
from chonoi.inventory import read_inventory, write_inventory
from chonoi.runner import Session


class Phase4(unittest.TestCase):
    def test_v13_roundtrip_preserves_spoilage_boundary(self):
        items = [{"id": "I2", "kind": "ca_loc", "fresh": 29.999999999999996},
                 {"id": "I1", "kind": "ca_linh", "fresh": 30}]
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "inventory.json")
            write_inventory(path, items, contract_version="1.3")
            actual = read_inventory(path, contract_version="1.3")
        self.assertEqual(actual, list(reversed(items)))
        self.assertLess(actual[1]["fresh"], 30)

    def test_ten_days_repeat_plans_and_preserve_ids_balances_and_upgrades(self):
        tuning = copy.deepcopy(load_contract()["tuning"])
        tuning["shop"]["max_ticks"] = 1
        scenario = {"day": {"money": 600, "earned": 600},
                    "gather": {"hold": [{"id": "I8", "kind": "ca_loc", "fresh": 100}],
                               "time_left_ticks": 1, "random_fish": False, "monsters": []},
                    "quan": {"time_left_ticks": 1, "random_customers": False}}
        s = Session("day", tuning, scenario, 7, days=10)
        controls = LiveInputs(BUTTONS_V11)
        seen = []
        for day in range(1, 11):
            self.assertEqual(s.sim.day_plan["dishes"], tuning["day_plan"][(day-1) % 5]["dishes"])
            seen.append(s.snapshot()["hold"][0]["id"])
            s.step(controls.advance())
            s.step(controls.advance())
            controls.set(buy="oxygen")
            events = s.step(controls.advance())
            self.assertTrue(any(e["name"] == "shop_end" for e in events))
        self.assertTrue(s.done)
        self.assertEqual(s.end_row()["days_completed"], 10)
        self.assertEqual(len(set(seen)), 10)
        self.assertEqual(s.sim.money, 0)
        self.assertEqual(s.sim.earned, 600)
        self.assertEqual(s.sim.active_upgrades["oxygen"], 2)

    def test_fps_uses_slowest_one_percent_frame_times(self):
        result = summarize([10] * 99 + [100], 1.09, 250)
        self.assertAlmostEqual(result["avg_fps"], 100/1.09)
        self.assertEqual(result["p1_low_fps"], 10)
        self.assertEqual(result["frames"], 100)

    def test_release_demo_serves_pays_buys_and_closes_shop(self):
        from chonoi.scenario import load_scenario
        tuning = load_contract()["tuning"]
        path = Path(__file__).resolve().parents[1] / "docs/scenarios/phase-4-demo.json"
        scenario = load_scenario(str(path), "day", tuning)
        session = Session("day", tuning, scenario, 42)
        controls = LiveInputs(BUTTONS_V11)
        events = []

        def step(**keys):
            controls.set(**keys)
            events.extend(session.step(controls.advance()))

        step(interact=True)  # Dock with a real gather -> quan transfer.
        step(interact=False)
        step(interact=True)  # Start cooking at B1.
        step(interact=False)
        while session.sim.child.stoves[0]["state"] != "ready":
            step()
        step(interact=True)
        step(interact=False)
        self.assertIsNotNone(session.snapshot()["hand"])
        for _ in range(240):
            x, z = session.sim.child.pos
            if (x-9)**2 + (z-2)**2 < .8**2:
                break
            dx, dz = 9-x, 2-z
            length = (dx*dx+dz*dz)**.5
            step(move=[dx/length, dz/length])
        step(move=[0, 0], interact=True)
        step(interact=False)
        while session.sim.phase != "shop":
            step()
        self.assertTrue(any(e["name"] == "served" for e in events))
        self.assertTrue(any(e["name"] == "paid" for e in events))
        self.assertGreater(session.sim.earned, 200)
        step(buy="oxygen", shop_done=True)
        self.assertTrue(session.done)
        self.assertEqual(session.end_row()["days_completed"], 1)
        self.assertEqual(session.sim.upgrades["oxygen"], 1)


if __name__ == "__main__":
    unittest.main()
