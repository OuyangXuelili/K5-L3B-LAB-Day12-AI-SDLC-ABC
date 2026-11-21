"""Hồi quy Ticket-03 trên luồng gather, quán, day và CLI v1.2."""

from pathlib import Path
import unittest

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.inputs import InputState
from chonoi.runner import Session
from helpers import Workdir, events, frames, individuals, read_jsonl, run_headless, snapshots, write_json


def press(*buttons):
    return InputState((0, 0), {}, set(buttons))


def item(ident, kind, fresh):
    return {"id": ident, "kind": kind, "fresh": fresh}


def order(ident="C1", table="T1", dish="ca_loc_nuong_trui", **fields):
    return dict(id=ident, table_id=table, dish_id=dish, **fields)


class Phase3(unittest.TestCase):
    def setUp(self):
        self.tuning = load_contract()["tuning"]

    def session(self, mode, scenario, days=1):
        return Session(mode, self.tuning, scenario, 7, days=days)

    def quan(self, **fixture):
        return self.session("quan", {"random_customers": False, **fixture})

    def test_spoiled_events_are_once_in_numeric_id_order_after_pause(self):
        hold = [item("I10", "ca_loc", 30.025), item("I2", "ca_linh", 30.025),
                item("I3", "bong_sung", 29)]
        s = self.session("gather", {"hold": hold, "nodes": [], "random_fish": False, "monsters": []})
        for _ in range(3):
            self.assertEqual(s.step(press()), [])
        self.assertEqual([i["fresh"] for i in s.snapshot()["hold"][:2]], [30.0, 30.0])
        paused = s.step(press("pause"))
        self.assertEqual([r["name"] for r in paused], ["paused"])
        self.assertEqual(s.step(press()), [])
        self.assertEqual(s.snapshot()["hold"][0]["fresh"], 30.0)
        resumed = s.step(press("pause"))
        self.assertEqual([r["name"] for r in resumed], ["resumed", "spoiled", "spoiled"])
        self.assertEqual([r["data"] for r in resumed[1:]], [
            {"item_id": "I2", "kind": "ca_linh", "location": "hold"},
            {"item_id": "I10", "kind": "ca_loc", "location": "hold"},
        ])
        self.assertEqual(s.snapshot()["hold_count"], 3)
        self.assertEqual(s.step(press()), [])

    def test_harvest_starts_fresh_and_ages_next_tick(self):
        s = self.session("gather", {"player": {"pos": [12, 0]}, "random_fish": False})
        self.assertEqual(s.step(press("interact"))[0]["name"], "gather")
        self.assertEqual(s.snapshot()["hold"], individuals("bong_dien_dien"))
        s.step(press())
        self.assertLess(s.snapshot()["hold"][0]["fresh"], 100)

    def test_day_keeps_exact_handoff_and_reissues_template_ids(self):
        hold = [item("I10", "ca_loc", 30.025), item("I2", "bong_sung", 60)]
        s = self.session("day", {"gather": {"hold": hold, "time_left_ticks": 1},
                                 "quan": {"time_left_ticks": 1}}, days=2)
        self.assertEqual(s.snapshot()["hold"], hold)
        events_at_dock = s.step(press("interact"))
        transfer = events_at_dock[0]["data"]["inventory"]["items"]
        self.assertEqual(transfer, s.snapshot()["stock"])
        self.assertEqual([i["id"] for i in transfer], ["I2", "I10"])
        self.assertAlmostEqual(transfer[1]["fresh"], 30.025 - 1 / 120)
        s.step(press())
        shop_stock = s.snapshot()["stock"]
        self.assertAlmostEqual(shop_stock[1]["fresh"], transfer[1]["fresh"] - 1 / 240)
        for _ in range(8):
            s.step(press())
        self.assertEqual(s.snapshot()["stock"], shop_stock)
        s.step(press("shop_done"))
        self.assertEqual(s.snapshot()["hold"], [item("I11", "ca_loc", 30.025), item("I12", "bong_sung", 60)])

    def test_initial_reservations_use_order_tick_table_freshness_and_numeric_id(self):
        s = self.quan(stock=[item("I10", "ca_loc", 80), item("I2", "ca_loc", 80),
                             item("I1", "ca_loc", 75), item("I3", "ca_loc", 29)],
                      customers=[order("C9", "T2"), order("C2", "T1"), order("C1", "T3", order_tick=1)])
        customers = {c["id"]: c for c in s.snapshot()["customers"]}
        self.assertEqual([customers[c]["reserved"] for c in ("C2", "C9", "C1")],
                         [["I2"], ["I10"], ["I1"]])
        self.assertEqual(s.snapshot()["available_stock"], {})

    def test_retry_releases_whole_recipe_uses_freshest_and_retries_only_once(self):
        s = self.quan(
            stock=[item("I10", "bong_sung", 30), item("I2", "bong_sung", 30),
                   item("I4", "bong_sung", 60), item("I5", "bong_sung", 90), item("I6", "bong_sung", 80)],
            customers=[order("C1", "T2", "goi_bong_sung", reserved=["I10", "I4"]),
                       order("C8", "T1", "goi_bong_sung", reserved=["I2", "I5"])])
        result = s.step(press())
        self.assertEqual([(r["name"], r["data"]["item_id"], r["data"]["location"]) for r in result],
                         [("spoiled", "I2", "stock"), ("spoiled", "I10", "stock")])
        first, second = s.snapshot()["customers"]
        self.assertEqual((second["id"], second["reserved"]), ("C8", ["I5", "I6"]))
        self.assertEqual((first["reserved"], first["order_status"]), ([], "unfulfillable"))
        self.assertEqual(s.snapshot()["available_stock"], {"bong_sung": 1})
        self.assertEqual(s.step(press()), [])
        self.assertEqual(s.snapshot()["customers"][0]["order_status"], "unfulfillable")

    def test_cook_uses_reserved_ids_exact_price_and_tip_later(self):
        s = self.quan(stock=[item("I10", "bong_sung", 50.5), item("I2", "bong_sung", 50.5),
                             item("I3", "bong_sung", 100)],
                      customers=[order(dish="goi_bong_sung", reserved=["I10", "I2"])],
                      player={"pos": [2, 8]})
        for _ in range(119):
            self.assertEqual(s.step(press()), [])
        cooked = s.step(press("interact"))[0]
        self.assertEqual(cooked["tick"], 120)
        self.assertEqual(cooked["data"], {"stove_id": "B1", "order_id": "C1", "dish_id": "goi_bong_sung",
                                         "base_price": 20, "items": [item("I2", "bong_sung", 50),
                                                                      item("I10", "bong_sung", 50)]})
        self.assertEqual([i["id"] for i in s.snapshot()["stock"]], ["I3"])
        for _ in range(239):
            s.step(press())
        s.step(press("interact"))
        self.assertEqual(s.snapshot()["hand"]["base_price"], 20)
        s.sim.pos = [9, 2]
        served = s.step(press("interact"))[0]
        self.assertEqual((served["data"]["price"], served["data"]["tip"]), (20, 4))

    def test_serving_on_patience_deadline_and_closing_uses_interaction_first(self):
        for closing in (False, True):
            with self.subTest(closing=closing):
                s = self.quan(player={"pos": [9, 2]}, time_left_ticks=1 if closing else 2,
                              customers=[order(order_status="assigned", patience_ticks_left=1)],
                              hand={"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 19})
                rows = s.step(press("interact"))
                expected = ["served", "paid", "quan_end"] if closing else ["served"]
                self.assertEqual([r["name"] for r in rows], expected)
                self.assertEqual(rows[0]["data"]["tip"], 0)
                if closing:
                    self.assertEqual(rows[1]["data"]["amount"], 19)

    def test_rejects_inconsistent_reserved_and_dish_fixtures(self):
        for reserved in (["I3"], ["missing"], ["I2", "I2"], ["I1", "I2"], {"ca_loc": 1}):
            with self.subTest(reserved=reserved), self.assertRaises(BadInput):
                self.quan(stock=[item("I1", "ca_loc", 60), item("I2", "ca_loc", 90), item("I3", "ca_loc", 29)],
                          customers=[order(reserved=reserved)])
        with self.assertRaises(BadInput):
            self.quan(stock=individuals("ca_loc"),
                      customers=[order("C1", "T1", reserved=["I1"]), order("C2", "T2", reserved=["I1"])])
        for price in (True, -1, 61, 19.5):
            with self.subTest(price=price), self.assertRaises(BadInput):
                self.quan(customers=[order(order_status="assigned")],
                          hand={"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": price})

    def test_cli_inventory_at_threshold_roundtrips_and_old_file_rejected(self):
        with Workdir() as work:
            stock = work.path("stock.json")
            gather = write_json(work.path("gather.json"), {"gather": {
                "hold": [item("I1", "ca_linh", 30), item("I2", "bong_sung", 30.025)],
                "random_fish": False, "monsters": []}})
            inputs = write_json(work.path("inputs.json"), frames({"tick": 0, "interact": True}))
            gout = work.path("gather.jsonl")
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "1",
                                     "--scenario", gather, "--inputs", inputs, "--out", gout,
                                     "--inventory-out", stock)
            self.assertEqual(code, 0, err)
            gather_rows = read_jsonl(gout)
            self.assertEqual(events(gather_rows, "spoiled")[0]["tick"], 1)
            items = read_jsonl(stock)[0]["items"]
            self.assertLess(items[0]["fresh"], 30)
            self.assertGreater(items[1]["fresh"], 30)
            self.assertEqual(events(gather_rows, "gather_end")[0]["data"]["inventory"]["items"], items)
            qout = work.path("quan.jsonl")
            code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0",
                                     "--inventory", stock, "--out", qout)
            self.assertEqual(code, 0, err)
            snapshot = snapshots(read_jsonl(qout))[0]
            self.assertEqual(snapshot["stock"], items)
            self.assertEqual(snapshot["available_stock"], {"bong_sung": 1})
            old = write_json(work.path("old.json"), {"items": {"ca_linh": 1}})
            before = Path(qout).read_bytes()
            code, _ = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0",
                                   "--inventory", old, "--out", qout)
            self.assertEqual(code, 2)
            self.assertEqual(Path(qout).read_bytes(), before)
