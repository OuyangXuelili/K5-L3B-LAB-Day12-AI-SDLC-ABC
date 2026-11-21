"""Ticket-02: biên tick/pause/shop/kho, cá bơi và va chạm; qua CLI khi cần."""
import copy
import json
import os
import unittest

from chonoi.contract import load_contract
from chonoi.inputs import BUTTONS_V11, InputPlayer, InputState, LiveInputs
from chonoi.runner import Session
from chonoi.live import LiveGame
from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json


def inp(*buttons, buy=None):
    return InputState((0, 0), {}, set(buttons), buy)


def monster(ident="M1", pos=None, **kw):
    pos = pos or [40, 15]
    return dict(id=ident, kind="ca_sau", pos=pos, waypoints=[[40, 15], [44, 15]], **kw)


class Phase2(unittest.TestCase):
    def setUp(self):
        self.t = copy.deepcopy(load_contract()["tuning"])

    def day(self, meta=None, gather=None, quan=None, days=1):
        return Session("day", self.t, {"day": meta or {}, "gather": gather or {"time_left_ticks": 1},
            "quan": quan or {"time_left_ticks": 1, "random_customers": False}}, 7, days=days)

    def test_day_changes_snapshot_phase_but_end_event_keeps_old_phase(self):
        s = self.day(gather={"hold": ["ca_keo", "keo_neo"], "time_left_ticks": 1})
        rows = s.step(inp())
        self.assertEqual([(r["phase"], r["name"]) for r in rows], [("gather", "gather_end"), ("quan", "phase_start")])
        snap = s.snapshot()
        self.assertEqual((snap["mode"], snap["phase"], snap["phase_tick"]), ("day", "quan", 0))
        self.assertEqual(snap["stock"], {"ca_keo": 1, "keo_neo": 1})
        s.step(inp())
        self.assertEqual(s.snapshot()["phase"], "shop")
        self.assertEqual(s.end_row()["days_completed"], 0)
        s.step(inp("shop_done"))
        self.assertEqual(s.end_row()["reason"], "days_complete")

    def test_shop_exact_funds_earned_unchanged_and_next_day_effective(self):
        s = self.day(meta={"money": 200, "earned": 200}, days=2)
        s.step(inp()); s.step(inp())
        s.step(inp(buy="oxygen"))
        snap = s.snapshot()
        self.assertEqual((snap["money"], snap["earned"], snap["score"]), (0, 200, 500))
        self.assertEqual(snap["upgrades"], {"oxygen": 1})
        self.assertEqual(snap["active_upgrades"], {})
        rows = s.step(inp("shop_done"))
        self.assertEqual(rows[0]["day"], 1)
        self.assertEqual(rows[-1]["day"], 2)
        self.assertEqual(s.snapshot()["player"]["oxygen_max_ticks"], 2700)
        self.assertEqual(s.snapshot()["player"]["oxygen_ticks"], 2700)

    def test_shop_failures_do_not_change_state(self):
        for meta, action, reason in (({}, "hp", "funds"), ({"upgrades": {"hp": 2}}, "hp", "max_level"), ({}, "vendor", "unknown")):
            s = self.day(meta=meta)
            s.step(inp()); s.step(inp())
            before = (s.sim.money, dict(s.sim.upgrades))
            rows = s.step(inp(buy=action))
            self.assertEqual(rows[0]["data"], {"action": action, "reason": reason})
            self.assertEqual((s.sim.money, s.sim.upgrades), before)

    def test_shop_timeout_includes_last_tick_purchase(self):
        s = self.day(meta={"money": 250, "earned": 250})
        s.step(inp()); s.step(inp())
        for _ in range(599):
            s.step(inp())
        self.assertFalse(s.done)
        rows = s.step(inp(buy="hp"))
        self.assertEqual([r["name"] for r in rows], ["bought", "shop_end"])
        self.assertEqual(rows[-1]["data"]["reason"], "time")
        self.assertEqual(s.end_row()["days_completed"], 1)

    def test_stock_is_discarded_after_shop_and_basket_is_new(self):
        s = self.day(gather={"hold": ["ca_loc"], "time_left_ticks": 1}, days=2)
        s.step(inp()); s.step(inp())
        self.assertEqual(s.snapshot()["stock"], {"ca_loc": 1})
        s.step(inp("shop_done"))
        self.assertEqual(s.sim.shop_stock, {})
        self.assertEqual(s.snapshot()["hold"], ["ca_loc"], "scenario template khởi tạo lại, không cộng kho dư")

    def test_pause_freezes_all_timers_and_consumes_action_edges(self):
        for mode, block in (("gather", {"player": {"pos": [20, 5], "oxygen_ticks": 2}, "random_fish": False}), ("quan", {"random_customers": False})):
            s = Session(mode, self.t, block, 1)
            player = InputPlayer([{"tick": 0, "pause": True, "interact": True}, {"tick": 1, "pause": False}, {"tick": 3, "pause": True}], BUTTONS_V11)
            before = s.sim.time_left_ticks
            for tick in range(3):
                s.step(player.advance(tick))
            self.assertEqual((s.tick, s.sim_tick, s.sim.time_left_ticks), (3, 0, before))
            self.assertEqual(s.snapshot()["state"], "paused")
            rows = s.step(player.advance(3))
            self.assertEqual(rows[0]["name"], "resumed")
            self.assertEqual(s.sim_tick, 1)
            self.assertFalse(s.done, "interact giữ true không sinh cạnh lúc resume")

    def test_pause_also_freezes_shop_and_ignores_purchase(self):
        s = self.day(meta={"money": 200, "earned": 200})
        s.step(inp()); s.step(inp())
        before = s.snapshot()["time_left_ticks"]
        s.step(inp("pause", buy="oxygen")); s.step(inp(buy="oxygen"))
        self.assertEqual(s.snapshot()["time_left_ticks"], before)
        self.assertEqual(s.sim.money, 200)
        s.step(inp("pause", buy="oxygen"))
        self.assertEqual(s.sim.money, 0)

    def test_buy_does_not_inherit_but_buttons_do(self):
        p = InputPlayer([{"tick": 0, "buy": "hp", "shop_done": True}], BUTTONS_V11)
        self.assertEqual(p.advance(0).buy, "hp")
        after = p.advance(1)
        self.assertIsNone(after.buy)
        self.assertFalse(after.pressed("shop_done"))
        live = LiveInputs(BUTTONS_V11)
        live.set(buy="oxygen")
        self.assertEqual(live.advance().buy, "oxygen")
        self.assertIsNone(live.advance().buy)

    def test_live_menu_intros_and_restart_share_session(self):
        g = LiveGame("day", self.t, {"gather": {"time_left_ticks": 1}, "quan": {"time_left_ticks": 1}}, 1)
        g._tick_once()
        self.assertEqual(g.session.tick, 0)
        g.set_input({"continue": True})
        self.assertEqual(g.screen, "DayIntro")
        for _ in range(240):
            g._tick_once()
        self.assertIsNone(g.screen)
        g._tick_once()
        self.assertEqual(g.screen, "EveningIntro")
        g.set_input({"continue": True}); g._tick_once()
        self.assertEqual(g.screen, "DayResult")
        g.set_input({"continue": True}); g.set_input({"shop_done": True}); g._tick_once()
        self.assertEqual(g.screen, "Summary")
        g.set_input({"menu": True})
        self.assertEqual(g.screen, "Menu")
        self.assertEqual(g.session.tick, 0)

    def test_fish_seed_initial_unique_and_spawns_after_swimming(self):
        a, b = Session("gather", self.t, {}, 7), Session("gather", self.t, {}, 7)
        self.assertEqual(a.snapshot(), b.snapshot())
        fish = a.snapshot()["fish"]
        self.assertEqual(len(fish), 8)
        self.assertEqual(len({tuple(f["pos"]) for f in fish}), 8)
        for _ in range(359):
            self.assertFalse(any(r["name"] == "fish_spawned" for r in a.step(inp())))
        rows = a.step(inp())
        self.assertEqual(rows[0]["name"], "fish_spawned")
        newest = max(a.sim.fish, key=lambda f: int(f["id"][1:]))
        self.assertEqual(newest["age_ticks"], 0)

    def test_random_fish_false_freezes_fixture_and_suppresses_spawns(self):
        s = Session("gather", self.t, {"random_fish": False, "fish": [{"id": "F9", "kind": "ca_keo", "pos": [40, 24]}]}, 1)
        before = copy.deepcopy(s.sim.fish)
        for _ in range(360):
            s.step(inp())
        self.assertEqual(s.sim.fish, before)

    def test_fish_reflects_remaining_distance_on_two_edges(self):
        s = Session("gather", self.t, {"fish": [{"id": "F1", "kind": "ca_keo", "pos": [95.99, 27.99], "heading_deg": 45}]}, 7)
        s.step(inp())
        fish = s.sim.fish[0]
        self.assertAlmostEqual(fish["pos"][0], 96 - (1.5 / 60 / 2**.5 - .01))
        self.assertAlmostEqual(fish["pos"][1], 28 - (1.5 / 60 / 2**.5 - .01))
        self.assertAlmostEqual(fish["heading_deg"], 225)

    def test_catch_uses_positions_before_fish_swim(self):
        s = Session("gather", self.t, {"player": {"pos": [40, 24]}, "monsters": [], "fish": [{"id": "F1", "kind": "ca_keo", "pos": [42, 24]}]}, 7)
        self.assertEqual(s.step(inp("catch"))[0]["name"], "fish_caught")
        self.assertEqual(s.sim.hold, ["ca_keo"] * 2)

    def test_monster_hit_lifo_recoil_invulnerability_and_faint_inventory(self):
        s = Session("gather", self.t, {"player": {"pos": [40, 15], "hp": 1}, "hold": ["ca_loc", "bong_sung", "keo_neo"], "monsters": [monster()], "random_fish": False}, 7)
        rows = s.step(inp("catch"))
        self.assertEqual([r["name"] for r in rows], ["monster_hit", "faint", "gather_end"])
        self.assertEqual(rows[0]["data"]["lost"], ["keo_neo"])
        self.assertEqual(rows[1]["data"], {"cause": "monster", "lost": ["bong_sung", "ca_loc"], "hp": 0})
        self.assertEqual(s.sim.inventory_items(), {})
        self.assertEqual(s.sim.monsters[0]["state_ticks_left"], 60)

    def test_invulnerability_does_not_trigger_recoil_and_choke_bypasses_it(self):
        s = Session("gather", self.t, {"player": {"pos": [40, 15], "invuln_ticks": 2, "oxygen_ticks": 0, "zero_oxy_ticks": 59}, "monsters": [monster()], "random_fish": False}, 1)
        self.assertEqual([r["name"] for r in s.step(inp())], ["choke"])
        self.assertEqual(s.sim.monsters[0]["state"], "chase")
        self.assertEqual([r["name"] for r in s.step(inp())], ["monster_hit"])

    def test_recoil_is_sixty_later_steps_and_hit_tie_uses_numeric_id(self):
        s = Session("gather", self.t, {"player": {"pos": [40, 15]}, "monsters": [monster("M10"), monster("M2")], "random_fish": False}, 1)
        rows = s.step(inp())
        self.assertEqual(rows[0]["data"]["monster_id"], "M2")
        m = next(m for m in s.sim.monsters if m["id"] == "M2")
        initial = list(m["pos"])
        for _ in range(59):
            s.step(inp())
        self.assertEqual((m["state"], m["state_ticks_left"]), ("recoil", 1))
        s.step(inp())
        self.assertEqual(m["state"], "patrol")
        self.assertAlmostEqual(m["pos"][0] - initial[0], 2)

    def test_third_day_adds_second_monster(self):
        s = self.day(days=3)
        for _ in range(2):
            s.step(inp()); s.step(inp()); s.step(inp("shop_done"))
        self.assertEqual(s.sim.day, 3)
        self.assertEqual([m["id"] for m in s.sim.child.monsters], ["M1", "M2"])

    def test_invalid_v11_fixtures_exit_two_without_touching_output(self):
        cases = [("day", {"day": {"money": 1}}), ("day", {"quan": {"stock": {}}}),
            ("day", {"quan": {"reputation": 3}}), ("day", {"day": {"upgrades": {"hp": 3}}}),
            ("day", {"day": {"day_plan": [{"day": 1, "dishes": {"lau_mam": 1}, "ingredients": {}}]}}),
            ("gather", {"gather": {"monsters": [monster(state="recoil")]}}),
            ("quan", {"quan": {"customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "order_status": "assigned"}]}}),
            ("quan", {"quan": {"stoves": [{"id": "B1", "cook_ticks_left": -1}]}})]
        with Workdir() as w:
            out = w.path("out.jsonl")
            for mode, block in cases:
                sc = write_json(w.path("sc.json"), block)
                code, err = run_headless("--mode", mode, "--seed", "1", "--ticks", "0", "--scenario", sc, "--out", out)
                self.assertEqual(code, 2, (block, err))
                self.assertFalse(os.path.exists(out))

    def test_cli_days_and_inventory_flags(self):
        with Workdir() as w:
            for mode, extra in (("quan", ["--days", "1"]), ("day", ["--days", "0"]), ("day", ["--days", "6"]), ("day", ["--inventory-out", w.path("i.json")])):
                code, _ = run_headless("--mode", mode, "--seed", "1", "--ticks", "0", "--out", w.path("out.jsonl"), *extra)
                self.assertEqual(code, 2)

    def test_phase_change_forces_snapshot_even_between_snapshot_intervals(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {"gather": {"time_left_ticks": 1}, "quan": {"time_left_ticks": 1}})
            out = w.path("o.jsonl")
            code, err = run_headless("--mode", "day", "--seed", "1", "--ticks", "3", "--scenario", sc, "--out", out, "--snapshot-every", "10")
            self.assertEqual(code, 0, err)
            snaps = snapshots(read_jsonl(out))
            self.assertIn((1, "quan", 0), [(s["tick"], s["phase"], s["phase_tick"]) for s in snaps])
            self.assertIn((2, "shop", 0), [(s["tick"], s["phase"], s["phase_tick"]) for s in snaps])
            self.assertEqual(len(snaps), len({s["tick"] for s in snaps}))

    def test_multi_day_cli_is_byte_identical_and_closes_last_shop(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {"gather": {"time_left_ticks": 1}, "quan": {"time_left_ticks": 1}})
            ins = write_json(w.path("i.json"), frames({"tick": 2, "buy": "oxygen", "shop_done": True}, {"tick": 3, "shop_done": False}, {"tick": 5, "shop_done": True}))
            data = []
            for n in range(2):
                path = w.path(f"{n}.jsonl")
                code, err = run_headless("--mode", "day", "--days", "2", "--seed", "8", "--ticks", "10", "--scenario", sc, "--inputs", ins, "--out", path, "--snapshot-every", "1")
                self.assertEqual(code, 0, err)
                with open(path, "rb") as f:
                    data.append(f.read())
            self.assertEqual(*data)
            rows = read_jsonl(w.path("0.jsonl"))
            self.assertEqual(rows[-1]["days_completed"], 2)
            self.assertEqual(rows[-1]["ticks"], 6)
            self.assertEqual(len(events(rows, "day_plan")), 2)
