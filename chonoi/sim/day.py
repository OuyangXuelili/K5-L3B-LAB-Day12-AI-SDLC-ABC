"""Điều phối một đến năm ngày; headless bỏ qua các màn giới thiệu."""
import copy

from ..planning import validate_plans
from ..scenario import _validate_block, validate_day
from .gather import GatherSim
from .quan import QuanSim


class DaySim:
    mode = "day"

    def __init__(self, tuning, scenario, streams, ids, days=1):
        self.tuning, self.scenario, self.rng, self.ids = tuning, copy.deepcopy(scenario), streams, ids
        meta = scenario.get("day", {})
        validate_day(meta, tuning)
        self.money, self.earned = meta.get("money", 0), meta.get("earned", 0)
        self.reputation = meta.get("reputation", tuning["quan"]["reputation_initial"])
        self.upgrades = dict(meta.get("upgrades", {}))
        self.active_upgrades = dict(self.upgrades)
        plans = {p["day"]: copy.deepcopy(p) for p in tuning["day_plan"]}
        plans.update({p["day"]: p for p in validate_plans(meta.get("day_plan", []), tuning["menu"])})
        self.plans = plans
        self.day, self.days, self.days_completed = 1, days, 0
        self.phase_tick = 0
        self.done, self.reason = False, None
        self.shop_stock = [] if "freshness" in self.tuning else {}
        self.results, self.sold = [], {}
        self._start_gather()

    @property
    def time_left_ticks(self):
        return self.child.time_left_ticks if self.phase != "shop" else self.shop_left

    def _start_gather(self):
        effective = copy.deepcopy(self.tuning)
        for kind, field in (("oxygen", "oxygen_max_s"), ("hp", "hp_max")):
            level = self.upgrades.get(kind, 0)
            if level:
                effective["gather"][field] = effective["shop"]["upgrades"][kind][level - 1][field]
        self.active_upgrades = dict(self.upgrades)
        block = copy.deepcopy(self.scenario.get("gather", {}))
        _validate_block(block, "gather", effective)
        if "freshness" in effective and self.day > 1:
            block["hold"] = [dict(item, id=self.ids.new("I")) for item in block.get("hold", [])]
        block["_day"] = self.day
        self.child = GatherSim(effective, block, self.rng, self.ids)
        self.child.money, self.child.earned, self.child.reputation = self.money, self.earned, self.reputation
        self.phase, self.phase_tick = "gather", 0
        self.day_plan = copy.deepcopy(self.plans[(self.day - 1) % len(self.tuning["day_plan"]) + 1])
        self.day_start_reputation = self.reputation

    def _event(self, name, data=None, phase=None, day=None):
        return {"phase": phase or self.phase, "day": self.day if day is None else day,
                "name": name, "data": {} if data is None else data}

    def initial_events(self):
        return [self._event("day_start"), self._event("day_plan", {k: self.day_plan[k] for k in ("dishes", "ingredients")}), self._event("phase_start")]

    def snapshot(self):
        state = self.child.snapshot() if self.phase != "shop" else {"stock": copy.deepcopy(self.shop_stock)}
        state.update(day=self.day, day_plan=copy.deepcopy(self.day_plan), upgrades=dict(self.upgrades),
                     active_upgrades=dict(self.active_upgrades), days_completed=self.days_completed,
                     day_results=copy.deepcopy(self.results), sold=dict(sorted(self.sold.items())))
        return state

    def step(self, inp):
        if self.done:
            return []
        self.phase_tick += 1
        if self.phase == "shop":
            return self._shop(inp)
        ev = [self._event(name, data) for name, data in self.child.step(inp)]
        self.money, self.earned, self.reputation = self.child.money, self.child.earned, self.child.reputation
        if not self.child.done:
            return ev
        if self.phase == "gather":
            inventory = self.child.hold if self.child.freshness else self.child.inventory_items()
            self.child = QuanSim(self.tuning, self.scenario.get("quan", {}), self.rng, self.ids,
                                 inventory=inventory, allowed_dishes=self.day_plan["dishes"])
            self.child.money, self.child.earned, self.child.reputation = self.money, self.earned, self.reputation
            self.phase, self.phase_tick = "quan", 0
        else:
            q = self.child
            self.shop_stock = q.stock_snapshot()
            self.results.append({"day": self.day, "served": q.served_count, "left": q.left_count,
                "shift_earned": q.shift_earned, "tips": q.tips, "reputation_delta": round(self.reputation - self.day_start_reputation, 10)})
            for dish, n in q.sold.items():
                self.sold[dish] = self.sold.get(dish, 0) + n
            self.phase, self.phase_tick = "shop", 0
            self.shop_left = self.tuning["shop"]["max_ticks"]
        ev.append(self._event("phase_start"))
        return ev

    def _shop(self, inp):
        events = []
        self.shop_left = max(0, self.shop_left - 1)
        if inp.buy is not None:
            action = inp.buy
            levels = self.tuning["shop"]["upgrades"].get(action)
            level = self.upgrades.get(action, 0)
            reason = "unknown" if levels is None else "max_level" if level >= len(levels) else None
            if reason is None:
                item = levels[level]
                if self.money < item["price"]:
                    reason = "funds"
                else:
                    self.money -= item["price"]
                    self.upgrades[action] = level + 1
                    events.append(self._event("bought", {"upgrade": action, "level": level + 1, "price": item["price"], "money": self.money}))
            if reason:
                events.append(self._event("buy_failed", {"action": action, "reason": reason}))
        if inp.pressed("shop_done") or self.shop_left == 0:
            reason = "done" if inp.pressed("shop_done") else "time"
            events.append(self._event("shop_end", {"reason": reason}))
            self.days_completed += 1
            self.shop_stock = [] if "freshness" in self.tuning else {}
            if self.days_completed == self.days:
                self.done, self.reason = True, "days_complete"
            else:
                self.day += 1
                self._start_gather()
                events.extend(self.initial_events())
        return events
