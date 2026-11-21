"""Kiểm luật gather theo PRD-0 / Test Contract v1.0, mục D–G trên lab board."""
import copy
import json
import os
import unittest

from chonoi.contract import load_contract, validate_tuning
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator, id_key
from chonoi.inputs import InputState, LiveInputs
from chonoi.rng import Streams
from chonoi.sim.gather import GatherSim
from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json


def input_state(*buttons, move=(0, 0)):
    return InputState(move, {b: True for b in buttons}, set(buttons))


def names(events_list):
    return [name for name, _ in events_list]


class GatherRules(unittest.TestCase):
    def setUp(self):
        self.tuning = copy.deepcopy(load_contract()["tuning"])

    def sim(self, **scenario):
        return GatherSim(self.tuning, scenario, Streams(7), IdAllocator())

    def test_underwater_oxygen_spends_one_tick(self):
        sim = self.sim(player={"pos": [20, 5]})
        start = sim.oxygen_ticks
        self.assertEqual(sim.step(input_state()), [])
        self.assertEqual(sim.oxygen_ticks, start - 1)

    def test_surface_refills_and_caps_oxygen(self):
        maximum = int(self.tuning["gather"]["oxygen_max_s"] * self.tuning["tick_hz"])
        sim = self.sim(player={"pos": [20, 0], "oxygen_ticks": maximum - 2})
        sim.step(input_state())
        self.assertEqual(sim.oxygen_ticks, maximum)
        sim.oxygen_ticks = 0
        sim.step(input_state())
        self.assertEqual(sim.oxygen_ticks, self.tuning["gather"]["oxygen_refill_per_tick"])

    def test_surface_depth_boundary_refills(self):
        sim = self.sim(player={"pos": [20, self.tuning["gather"]["surface_depth"]], "oxygen_ticks": 0})
        sim.step(input_state())
        self.assertGreater(sim.oxygen_ticks, 0)
        self.assertEqual(sim.zero_oxy_ticks, 0)

    def test_oxygen_empty_is_emitted_only_on_transition(self):
        sim = self.sim(player={"pos": [20, 5], "oxygen_ticks": 1})
        self.assertEqual(sim.step(input_state()), [("oxygen_empty", {"oxygen_ticks": 0})])
        self.assertEqual(sim.zero_oxy_ticks, 1)
        self.assertNotIn("oxygen_empty", names(sim.step(input_state())))

    def test_choke_at_configured_interval(self):
        sim = self.sim(player={"pos": [20, 5], "oxygen_ticks": 0})
        interval = self.tuning["gather"]["choke_interval_ticks"]
        for _ in range(interval - 1):
            self.assertNotIn("choke", names(sim.step(input_state())))
        self.assertIn("choke", names(sim.step(input_state())))
        self.assertEqual(sim.hp, self.tuning["gather"]["hp_max"] - 1)
        self.assertEqual(sim.zero_oxy_ticks, 0)

    def test_choke_uses_tuning_instead_of_fixed_second(self):
        self.tuning["gather"]["choke_interval_ticks"] = 3
        sim = self.sim(player={"pos": [20, 5], "oxygen_ticks": 0})
        sim.step(input_state())
        sim.step(input_state())
        self.assertEqual(names(sim.step(input_state())), ["choke"])

    def test_faint_clears_hold_and_prevents_other_actions(self):
        interval = self.tuning["gather"]["choke_interval_ticks"]
        sim = self.sim(player={"pos": [20, 5], "oxygen_ticks": 0, "hp": 1,
                               "zero_oxy_ticks": interval - 1},
                       hold=["ca_loc"], fish=[{"id": "F1", "kind": "ca_loc", "pos": [20, 5]}])
        result = sim.step(input_state("interact", "catch"))
        self.assertEqual(names(result), ["choke", "faint", "gather_end"])
        self.assertEqual(result[1][1], {"cause": "choke", "lost": ["ca_loc"], "hp": 0})
        self.assertEqual(result[-1][1], {"reason": "fainted", "inventory": {"items": {}}})
        self.assertTrue(sim.done)
        self.assertEqual(sim.hold, [])
        self.assertEqual(len(sim.fish), 1)
        self.assertEqual(sim.step(input_state("catch")), [])

    def test_dive_and_surface_use_positions_after_movement(self):
        boundary = self.tuning["gather"]["surface_depth"]
        sim = self.sim(player={"pos": [20, boundary]})
        result = sim.step(input_state(move=(0, 1)))
        self.assertEqual(names(result), ["dive"])
        self.assertGreater(sim.pos[1], boundary)
        self.assertEqual(result[0][1]["pos"], sim.pos)
        sim.vel = [0, 0]
        sim._tgt, sim._ramp_left = None, 0
        sim.pos[1] = boundary + 0.001
        sim.zero_oxy_ticks = 12
        sim.oxygen_ticks = 0
        result = sim.step(input_state(move=(0, -1)))
        self.assertEqual(names(result), ["surface"])
        self.assertGreater(sim.oxygen_ticks, 0)
        self.assertEqual(sim.zero_oxy_ticks, 0)

    def test_nearest_ready_node_with_numeric_tie_break(self):
        sim = self.sim(player={"pos": [20, 0]}, nodes=[
            {"id": "N10", "kind": "bong_sung", "pos": [21, 0]},
            {"id": "N2", "kind": "bong_dien_dien", "pos": [19, 0]},
            {"id": "N1", "kind": "bong_sung", "pos": [20, 0], "regrow_ticks": 10},
        ])
        result = sim.step(input_state("interact"))
        self.assertEqual(names(result), ["gather"])
        self.assertEqual(result[0][1]["node_id"], "N2")
        self.assertEqual(result[0][1], {"node_id": "N2", "kind": "bong_dien_dien", "amount": 1})
        self.assertEqual(sim.hold, ["bong_dien_dien"])
        node = next(n for n in sim.nodes if n["id"] == "N2")
        self.assertEqual(node["regrow_ticks"], int(self.tuning["gather"]["regrow_s"] * self.tuning["tick_hz"]))

    def test_gather_requires_surface_and_radius(self):
        sim = self.sim(player={"pos": [20, 5]}, nodes=[
            {"id": "N1", "kind": "bong_sung", "pos": [20, 0]},
        ])
        self.assertNotIn("gather", names(sim.step(input_state("interact"))))
        sim.pos = [50, 0]
        self.assertNotIn("gather", names(sim.step(input_state("interact"))))

    def test_ready_node_can_be_gathered_on_regrowth_tick(self):
        sim = self.sim(player={"pos": [20, 0]}, nodes=[
            {"id": "N1", "kind": "bong_sung", "pos": [20, 0], "regrow_ticks": 1},
        ])
        self.assertEqual(names(sim.step(input_state("interact"))), ["node_regrown", "gather"])

    def test_gather_full_does_not_consume_node(self):
        full = ["ca_loc"] * self.tuning["gather"]["hold_capacity"]
        sim = self.sim(player={"pos": [20, 0]}, hold=full,
                       nodes=[{"id": "N1", "kind": "bong_sung", "pos": [20, 0]}])
        self.assertEqual(sim.step(input_state("interact")), [("hold_full", {
            "action": "gather", "node_id": "N1", "required": 1, "free": 0,
        })])
        self.assertEqual(sim.hold, full)
        self.assertEqual(sim.nodes[0]["regrow_ticks"], 0)

    def test_catch_removes_one_nearest_school_and_sets_cooldown(self):
        sim = self.sim(player={"pos": [20, 5]}, fish=[
            {"id": "F10", "kind": "ca_loc", "pos": [21, 5]},
            {"id": "F2", "kind": "ca_linh", "pos": [19, 5]},
        ])
        result = sim.step(input_state("catch"))
        self.assertEqual(names(result), ["fish_caught"])
        self.assertEqual(result[0][1]["fish_id"], "F2")
        self.assertEqual(result[0][1], {"fish_id": "F2", "kind": "ca_linh", "yield": 3})
        self.assertEqual(sim.hold, ["ca_linh"] * self.tuning["gather"]["fish_yield"]["ca_linh"])
        self.assertEqual([f["id"] for f in sim.fish], ["F10"])
        self.assertEqual(sim.catch_cd_ticks, int(self.tuning["gather"]["catch_cooldown_s"] * self.tuning["tick_hz"]))

    def test_catch_requires_underwater_radius_and_cooldown(self):
        sim = self.sim(player={"pos": [20, 0]}, fish=[{"id": "F1", "kind": "ca_loc", "pos": [20, 1]}])
        self.assertNotIn("fish_caught", names(sim.step(input_state("catch"))))
        sim.pos = [20, 5]
        self.assertNotIn("fish_caught", names(sim.step(input_state("catch"))))
        sim.pos = [20, 1]
        sim.catch_cd_ticks = 2
        self.assertNotIn("fish_caught", names(sim.step(input_state("catch"))))
        self.assertEqual(names(sim.step(input_state("catch"))), ["fish_caught"])

    def test_catch_insufficient_space_is_atomic(self):
        initial = ["ca_loc"] * (self.tuning["gather"]["hold_capacity"] - 1)
        sim = self.sim(player={"pos": [20, 5]}, hold=initial,
                       fish=[{"id": "F1", "kind": "ca_linh", "pos": [20, 5]}])
        self.assertEqual(sim.step(input_state("catch")), [("hold_full", {
            "action": "catch", "fish_id": "F1", "required": 3, "free": 1,
        })])
        self.assertEqual(sim.hold, initial)
        self.assertEqual(len(sim.fish), 1)
        self.assertEqual(sim.catch_cd_ticks, 0)

    def test_hold_preserves_pickup_order_and_exact_capacity(self):
        capacity = self.tuning["gather"]["hold_capacity"]
        initial = ["bong_sung"] * (capacity - 1)
        sim = self.sim(player={"pos": [20, 5]}, hold=initial,
                       fish=[{"id": "F1", "kind": "ca_loc", "pos": [20, 5]}])
        self.assertEqual(names(sim.step(input_state("catch"))), ["fish_caught"])
        self.assertEqual(sim.hold, initial + ["ca_loc"])
        self.assertEqual(sim.hold.pop(), "ca_loc")

    def test_held_interact_does_not_repeat_gather(self):
        self.tuning["gather"]["regrow_s"] = 1 / self.tuning["tick_hz"]
        sim = self.sim(player={"pos": [20, 0]}, nodes=[{"id": "N1", "kind": "bong_sung", "pos": [20, 0]}])
        inputs = LiveInputs()
        inputs.set(interact=True)
        sim.step(inputs.advance())
        sim.step(inputs.advance())
        self.assertEqual(len(sim.hold), 1)
        inputs.set(interact=False)
        sim.step(inputs.advance())
        inputs.set(interact=True)
        sim.step(inputs.advance())
        self.assertEqual(len(sim.hold), 2)

    def test_dock_precedes_gather_and_time(self):
        dock = self.tuning["gather"]["dock_pos"]
        sim = self.sim(time_left_ticks=1, nodes=[{"id": "N1", "kind": "bong_sung", "pos": dock}])
        self.assertEqual(names(sim.step(input_state("interact"))), ["gather_end"])
        self.assertEqual(sim.reason, "docked")
        self.assertEqual(sim.hold, [])

    def test_tick_hz_is_read_from_contract(self):
        self.tuning["tick_hz"] = 30
        sim = self.sim(player={"pos": [20, 5]})
        self.assertEqual(sim.oxygen_max, self.tuning["gather"]["oxygen_max_s"] * 30)
        self.assertEqual(sim.time_left_ticks, self.tuning["gather"]["duration_s"] * 30)

    def test_faint_reports_loss_in_lifo_order(self):
        hold = ["ca_loc", "bong_sung", "ca_linh"]
        sim = self.sim(player={"pos": [20, 5], "oxygen_ticks": 0, "hp": 1, "zero_oxy_ticks": 59}, hold=hold)
        result = sim.step(input_state())
        self.assertEqual(result[1], ("faint", {"cause": "choke", "lost": hold[::-1], "hp": 0}))

    def test_surface_on_choke_deadline_prevents_damage(self):
        boundary = self.tuning["gather"]["surface_depth"]
        sim = self.sim(player={"pos": [20, boundary + 0.001], "oxygen_ticks": 0,
                               "zero_oxy_ticks": 59, "hp": 1})
        result = sim.step(input_state(move=(0, -1)))
        self.assertEqual(names(result), ["surface"])
        self.assertEqual(sim.hp, 1)
        self.assertEqual(sim.zero_oxy_ticks, 0)

    def test_full_nearest_school_does_not_fall_back_to_smaller_yield(self):
        sim = self.sim(player={"pos": [20, 5]},
                       hold=["bong_sung"] * (self.tuning["gather"]["hold_capacity"] - 1),
                       fish=[{"id": "F1", "kind": "ca_linh", "pos": [20, 5]},
                             {"id": "F2", "kind": "ca_loc", "pos": [21, 5]}])
        result = sim.step(input_state("catch"))
        self.assertEqual(result[0][1]["fish_id"], "F1")
        self.assertEqual(len(sim.fish), 2)
        self.assertEqual(sim.catch_cd_ticks, 0)

    def test_last_tick_catch_is_in_final_inventory(self):
        sim = self.sim(player={"pos": [20, 5]}, time_left_ticks=1,
                       fish=[{"id": "F1", "kind": "ca_loc", "pos": [20, 5]}])
        result = sim.step(input_state("catch"))
        self.assertEqual(names(result), ["fish_caught", "gather_end"])
        self.assertEqual(result[-1][1], {"reason": "time", "inventory": {"items": {"ca_loc": 1}}})

    def test_inclusive_harvest_and_catch_radius(self):
        for action in ("gather", "catch"):
            with self.subTest(action=action):
                radius = self.tuning["gather"]["interact_radius" if action == "gather" else "catch_radius"]
                depth = 0 if action == "gather" else 5
                entities = {"nodes": [{"id": "N1", "kind": "bong_sung", "pos": [20 + radius, depth]}]} if action == "gather" else {
                    "fish": [{"id": "F1", "kind": "ca_loc", "pos": [20 + radius, depth]}]}
                sim = self.sim(player={"pos": [20, depth]}, **entities)
                result = sim.step(input_state("interact" if action == "gather" else "catch"))
                self.assertEqual(names(result), ["gather" if action == "gather" else "fish_caught"])


class GatherHeadless(unittest.TestCase):
    def test_invalid_gather_fixture_fails_before_writing_either_output(self):
        invalid = [
            {"player": {"invuln_ticks": 1}},
            {"player": {"heading_deg": float("nan")}},
            {"player": {"vel": [float("inf"), 0]}},
            {"player": {"oxygen_ticks": 1, "zero_oxy_ticks": 1}},
            {"player": {"pos": [20, 0], "oxygen_ticks": 0, "zero_oxy_ticks": 1}},
            {"player": {"pos": [20, 5], "oxygen_ticks": 0, "zero_oxy_ticks": 60}},
            {"nodes": [{"id": "N1", "kind": "bong_sung", "pos": [20, 0], "future_field": 1}]},
            {"fish": [{"id": "F1", "kind": "ca_loc", "pos": [20, 5], "future_field": 1}]},
            {"fish": [{"id": "F1", "kind": "ca_loc", "pos": [20, 5], "heading_deg": float("inf")}]},
        ]
        with Workdir() as w:
            for index, block in enumerate(invalid):
                with self.subTest(case=index):
                    scenario = write_json(w.path("invalid.json"), {"gather": block})
                    out, inventory = w.path("out.jsonl"), w.path("stock.json")
                    code, _ = run_headless("--mode", "gather", "--seed", "1", "--ticks", "0",
                                           "--scenario", scenario, "--out", out, "--inventory-out", inventory)
                    self.assertEqual(code, 2)
                    self.assertFalse(os.path.exists(out))
                    self.assertFalse(os.path.exists(inventory))

    def test_event_tick_and_payload_follow_contract(self):
        with Workdir() as w:
            scenario = write_json(w.path("scenario.json"), {"gather": {
                "player": {"pos": [20, 5], "oxygen_ticks": 1, "hp": 1},
                "hold": ["ca_loc", "bong_sung"], "nodes": [], "fish": [],
            }})
            code, error = run_headless("--mode", "gather", "--seed", "1", "--ticks", "100",
                                       "--scenario", scenario, "--out", w.path("out.jsonl"))
            self.assertEqual(code, 0, error)
            rows = read_jsonl(w.path("out.jsonl"))
            empty = events(rows, "oxygen_empty")
            self.assertEqual(empty[0]["tick"], 1)
            self.assertEqual(empty[0]["data"], {"oxygen_ticks": 0})
            self.assertEqual(events(rows, "choke")[0]["tick"], 60)
            self.assertEqual(events(rows, "faint")[0]["data"], {
                "cause": "choke", "lost": ["bong_sung", "ca_loc"], "hp": 0,
            })
            self.assertEqual(rows[-1]["reason"], "fainted")
            self.assertEqual(rows[-1]["ticks"], 60)
            self.assertEqual(len([r for r in snapshots(rows) if r["tick"] == 60]), 1)

    def test_real_gather_inventory_is_read_by_quan(self):
        with Workdir() as w:
            scenario = write_json(w.path("scenario.json"), {"gather": {
                "player": {"pos": [5, 0]}, "nodes": [{"id": "N1", "kind": "bong_sung", "pos": [5, 0]}],
                "fish": [],
            }})
            inputs = write_json(w.path("inputs.json"), frames(
                {"tick": 0, "move": [1, 0], "interact": True},
                {"tick": 1, "move": [-1, 0], "interact": False},
                {"tick": 10, "move": [0, 0], "interact": True},
            ))
            inventory = w.path("inventory.json")
            code, error = run_headless("--mode", "gather", "--seed", "7", "--ticks", "20",
                                       "--scenario", scenario, "--inputs", inputs,
                                       "--out", w.path("gather.jsonl"), "--inventory-out", inventory)
            self.assertEqual(code, 0, error)
            rows = read_jsonl(w.path("gather.jsonl"))
            self.assertEqual(len(events(rows, "gather")), 1)
            self.assertEqual(len(events(rows, "gather_end")), 1)
            with open(inventory, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": {"bong_sung": 1}})
            code, error = run_headless("--mode", "quan", "--seed", "7", "--ticks", "0",
                                       "--inventory", inventory, "--out", w.path("quan.jsonl"))
            self.assertEqual(code, 0, error)
            self.assertEqual(snapshots(read_jsonl(w.path("quan.jsonl")))[0]["stock"], {"bong_sung": 1})

    def test_faint_writes_empty_inventory_once(self):
        with Workdir() as w:
            scenario = write_json(w.path("scenario.json"), {"gather": {
                "player": {"pos": [20, 5], "oxygen_ticks": 0, "zero_oxy_ticks": 59, "hp": 1},
                "hold": ["ca_loc"],
            }})
            inventory = w.path("inventory.json")
            code, error = run_headless("--mode", "gather", "--seed", "1", "--ticks", "100",
                                       "--scenario", scenario, "--inventory-out", inventory,
                                       "--out", w.path("out.jsonl"))
            self.assertEqual(code, 0, error)
            rows = read_jsonl(w.path("out.jsonl"))
            self.assertEqual(len(events(rows, "faint")), 1)
            self.assertEqual(len(events(rows, "gather_end")), 1)
            with open(inventory, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": {}})

    def test_gameplay_replay_is_byte_identical_with_unsorted_entities(self):
        with Workdir() as w:
            scenario = write_json(w.path("scenario.json"), {"gather": {
                "player": {"pos": [20, 5]}, "time_left_ticks": 60,
                "fish": [{"id": "F10", "kind": "ca_loc", "pos": [21, 5]},
                         {"id": "F2", "kind": "ca_linh", "pos": [19, 5]}],
            }})
            inputs = write_json(w.path("inputs.json"), frames(
                {"tick": 0, "catch": True}, {"tick": 1, "catch": False}, {"tick": 30, "catch": True},
            ))
            outputs = []
            for index in range(2):
                path = w.path(f"run-{index}.jsonl")
                code, error = run_headless("--mode", "gather", "--seed", "42", "--ticks", "100",
                                           "--scenario", scenario, "--inputs", inputs, "--out", path)
                self.assertEqual(code, 0, error)
                with open(path, "rb") as f:
                    outputs.append(f.read())
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(len(events(read_jsonl(w.path("run-0.jsonl")), "fish_caught")), 2)


class GatherContractEdges(unittest.TestCase):
    def test_numeric_id_suffix_is_ascii_only(self):
        self.assertEqual(id_key("F٢"), ("F٢", -1, "F٢"))
        self.assertEqual(id_key("F2"), ("F", 2, "F2"))
        ids = IdAllocator()
        ids.reserve("F٢")
        self.assertEqual(ids.new("F"), "F1")

    def test_headless_rate_is_fixed_at_sixty(self):
        for hz in (30, True, None):
            with self.subTest(hz=hz):
                tuning = copy.deepcopy(load_contract()["tuning"])
                tuning["tick_hz"] = hz
                with self.assertRaises(BadInput):
                    validate_tuning(tuning)

    def test_contract_rejects_nonfinite_numeric_values(self):
        for path in (("gather", "swim_speed"), ("gather", "start_heading_deg"),
                     ("quan", "tip_rate")):
            with self.subTest(path=path):
                tuning = copy.deepcopy(load_contract()["tuning"])
                tuning[path[0]][path[1]] = float("inf")
                with self.assertRaises(BadInput):
                    validate_tuning(tuning)


if __name__ == "__main__":
    unittest.main()
