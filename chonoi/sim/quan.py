"""Buổi tối: giữ nguyên liệu theo đơn, nấu, phục vụ, thu tiền (Ticket-02)."""
import copy
import math

from ..errors import BadInput
from ..ids import id_key, sort_by_id
from .ramp import ramp_velocity


class QuanSim:
    mode = phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None, allowed_dishes=None):
        self.t, self.hz, self.menu = tuning["quan"], tuning["tick_hz"], tuning["menu"]
        self.allowed_dishes = set(self.menu if allowed_dishes is None else allowed_dishes)
        self.rng, self.ids, self.tick = streams, ids, 0
        self.random_customers = scenario.get("random_customers", True)
        p = scenario.get("player", {})
        self.pos = list(p.get("pos", self.t["start_pos"]))
        self.vel = list(p.get("vel", [0.0, 0.0]))
        self._tgt, self._ramp_left = None, 0
        self.stock = dict(inventory if inventory is not None else scenario.get("stock", {}))
        self.hand = copy.deepcopy(scenario.get("hand"))
        self.time_left_ticks = scenario.get("time_left_ticks", round(self.t["duration_s"] * self.hz))
        self.reputation = scenario.get("reputation", self.t["reputation_initial"])
        self.stoves = [dict(s, state=s.get("state", "idle"), dish=copy.deepcopy(s.get("dish")),
                            cook_ticks_left=s.get("cook_ticks_left", 0), ready_ticks=s.get("ready_ticks", 0))
                       for s in self._merge(self.t["stoves"], scenario.get("stoves", []))]
        self.tables = self._merge(self.t["tables"], scenario.get("tables", []))
        self.customers = []
        for source in scenario.get("customers", []):
            c = copy.deepcopy(source)
            c.setdefault("state", "waiting")
            c.setdefault("order_id", c["id"])
            c.setdefault("order_tick", 0)
            c.setdefault("patience_ticks_left", round(self.t["patience_s"] * self.hz))
            c.setdefault("order_status", "reserved" if c["state"] == "waiting" else "assigned")
            reserved = (dict(self.menu.get(c.get("dish_id"), {}).get("recipe", {}))
                        if c["state"] == "waiting" and c["order_status"] == "reserved" else {})
            if "reserved" in c and c["reserved"] != reserved:
                raise BadInput("reserved mâu thuẫn công thức/trạng thái đơn")
            c["reserved"] = reserved
            self.customers.append(c)
            ids.reserve(c["id"])
            ids.reserve(c["order_id"])
        self.money = self.earned = self.shift_earned = 0
        self.served_count = self.left_count = self.tips = 0
        self.sold = {}
        self.done, self.reason = False, None
        self._validate_orders()

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(copy.deepcopy(u))
        return sort_by_id(list(by_id.values()))

    def _validate_orders(self):
        occupied, orders = set(), set()
        for c in self.customers:
            if c.get("table_id") not in {t["id"] for t in self.tables} or c["table_id"] in occupied:
                raise BadInput("khách phải có bàn duy nhất")
            occupied.add(c["table_id"])
            if c.get("dish_id") not in self.allowed_dishes or c["order_id"] in orders:
                raise BadInput("món không thuộc thực đơn/kế hoạch hoặc trùng order_id")
            orders.add(c["order_id"])
            if c["state"] not in ("waiting", "eating") or c["order_status"] not in ("reserved", "assigned", "unfulfillable"):
                raise BadInput("trạng thái khách/đơn không hợp lệ")
            if c["state"] == "eating":
                if not {"eat_ticks_left", "price", "tip"} <= set(c) or c["order_status"] != "assigned":
                    raise BadInput("khách eating cần eat_ticks_left/price/tip và assigned")
                if c["price"] != self.menu[c["dish_id"]]["price"] or c["tip"] not in (0, math.floor(c["price"] * self.t["tip_rate"])):
                    raise BadInput("giá/boa khách eating mâu thuẫn thực đơn")
        if any(n < 0 for n in self.available_stock().values()):
            raise BadInput("giữ nguyên liệu vượt kho")
        dishes = ([self.hand] if self.hand is not None else [])
        for s in self.stoves:
            if s["state"] not in ("idle", "cooking", "ready"):
                raise BadInput("trạng thái bếp không hợp lệ")
            if s["state"] == "idle":
                if s["dish"] is not None or s["cook_ticks_left"] or s["ready_ticks"]:
                    raise BadInput("bếp idle không được có món/bộ đếm")
            else:
                if s["dish"] is None or (s["state"] == "cooking" and s["cook_ticks_left"] <= 0) or (s["state"] == "ready" and s["cook_ticks_left"]):
                    raise BadInput("bếp và bộ đếm/món mâu thuẫn")
                dishes.append(s["dish"])
        counts = {}
        for dish in dishes:
            if not isinstance(dish, dict) or set(dish) != {"order_id", "dish_id"}:
                raise BadInput("dish phải có order_id và dish_id")
            matches = [c for c in self.customers if c["order_id"] == dish["order_id"]]
            if len(matches) != 1 or matches[0]["state"] != "waiting" or matches[0]["order_status"] != "assigned" or matches[0]["dish_id"] != dish["dish_id"]:
                raise BadInput("món phải thuộc đúng đơn assigned đang chờ")
            counts[dish["order_id"]] = counts.get(dish["order_id"], 0) + 1
        for c in self.customers:
            expected = int(c["state"] == "waiting" and c["order_status"] == "assigned")
            if counts.get(c["order_id"], 0) != expected:
                raise BadInput("đơn assigned phải có đúng một món ở bếp hoặc trên tay")

    def available_stock(self):
        available = dict(self.stock)
        for c in self.customers:
            for k, amount in c["reserved"].items():
                available[k] = available.get(k, 0) - amount
        return available

    def snapshot(self):
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        return copy.deepcopy({"player": {"pos": self.pos, "vel": self.vel},
            "stock": {k: v for k, v in sorted(self.stock.items()) if v > 0},
            "available_stock": {k: v for k, v in sorted(self.available_stock().items()) if v > 0},
            "hand": self.hand, "stoves": self.stoves,
            "tables": [dict(tb, customer_id=occupied.get(tb["id"])) for tb in self.tables],
            "customers": sort_by_id(self.customers), "shift_earned": self.shift_earned,
            "served_count": self.served_count, "left_count": self.left_count, "tips": self.tips})

    def _rep(self, delta):
        self.reputation = min(self.t["reputation_max"], max(self.t["reputation_min"], round(self.reputation + delta, 10)))

    def _pay(self, c, events):
        amount = c["price"] + c["tip"]
        self.money += amount
        self.earned += amount
        self.shift_earned += amount
        self.tips += c["tip"]
        self.sold[c["dish_id"]] = self.sold.get(c["dish_id"], 0) + 1
        if c["tip"] > 0:
            self._rep(self.t["tip_reputation"])
        events.append(("paid", {"customer_id": c["id"], "table_id": c["table_id"], "order_id": c["order_id"],
            "dish_id": c["dish_id"], "price": c["price"], "tip": c["tip"], "amount": amount,
            "money": self.money, "reputation": self.reputation}))
        self.customers.remove(c)

    @staticmethod
    def _clear_stove(s):
        s.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)

    def _leave(self, c, reason, events):
        for s in self.stoves:
            if s["dish"] and s["dish"]["order_id"] == c["order_id"]:
                self._clear_stove(s)
        if self.hand and self.hand["order_id"] == c["order_id"]:
            self.hand = None
        if reason == "patience":
            self.left_count += 1
            self._rep(self.t["left_reputation_delta"])
        events.append(("customer_left", {"customer_id": c["id"], "table_id": c["table_id"],
            "order_id": c["order_id"], "reason": reason, "reputation": self.reputation}))
        self.customers.remove(c)

    def step(self, inp):
        if self.done:
            return []
        events = []
        self.tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        for c in sort_by_id(self.customers):
            field = "eat_ticks_left" if c["state"] == "eating" else "patience_ticks_left"
            c[field] = max(0, c[field] - 1)
        for s in self.stoves:
            if s["state"] == "cooking":
                s["cook_ticks_left"] -= 1
                if s["cook_ticks_left"] == 0:
                    s.update(state="ready", ready_ticks=0)
                    events.append(("dish_ready", dict(stove_id=s["id"], **s["dish"])))
            elif s["state"] == "ready":
                s["ready_ticks"] += 1
        for c in sort_by_id(self.customers):
            if c["state"] == "eating" and c["eat_ticks_left"] == 0:
                self._pay(c, events)
            elif c["state"] == "waiting" and c["patience_ticks_left"] == 0 and self.time_left_ticks > 0:
                self._leave(c, "patience", events)
        self._move(inp)
        if inp.pressed("interact"):
            self._interact(events)
        if self.time_left_ticks == 0:
            for c in sort_by_id(self.customers):
                if c["state"] == "eating":
                    self._pay(c, events)
                else:
                    self._leave(c, "closing", events)
            for s in self.stoves:
                self._clear_stove(s)
            self.hand = None
            self.done, self.reason = True, "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                "shift_earned": self.shift_earned, "reputation": self.reputation}))
        elif self.random_customers and self.tick >= self.t["first_customer_tick"] and (self.tick - self.t["first_customer_tick"]) % round(self.t["customer_interval_s"] * self.hz) == 0:
            self._arrive(events)
        return events

    def _arrive(self, events):
        occupied = {c["table_id"] for c in self.customers}
        free = [tb for tb in self.tables if tb["id"] not in occupied]
        if not free:
            return
        table, stock = free[0], self.available_stock()
        choices = sorted(d for d in self.allowed_dishes if all(stock.get(k, 0) >= n for k, n in self.menu[d]["recipe"].items()))
        if not choices:
            events.append(("no_dish", {"table_id": table["id"]}))
            return
        dish, ident = self.rng.get("customer_order").choice(choices), self.ids.new("C")
        c = {"id": ident, "table_id": table["id"], "order_id": ident, "dish_id": dish,
             "state": "waiting", "order_status": "reserved", "order_tick": self.tick,
             "patience_ticks_left": round(self.t["patience_s"] * self.hz), "reserved": dict(self.menu[dish]["recipe"])}
        self.customers.append(c)
        events.append(("customer_arrived", {"customer_id": ident, "table_id": table["id"], "order_id": ident,
            "dish_id": dish, "order_tick": self.tick}))

    def _interact(self, events):
        candidates = [(math.dist(self.pos, e["pos"]), priority, id_key(e["id"]), e)
                      for priority, entities in enumerate((self.stoves, self.tables)) for e in entities]
        candidates = [c for c in candidates if c[0] <= self.t["interact_radius"]]
        if not candidates:
            return
        _, priority, _, target = min(candidates, key=lambda c: c[:3])
        if priority == 0:
            s = target
            if s["state"] == "ready" and self.hand is None:
                self.hand = dict(s["dish"])
                events.append(("dish_picked", dict(stove_id=s["id"], **self.hand)))
                self._clear_stove(s)
            elif s["state"] == "idle" and self.hand is None:
                orders = [c for c in self.customers if c["state"] == "waiting" and c["order_status"] == "reserved"]
                if not orders:
                    return
                c = min(orders, key=lambda c: (c["order_tick"], id_key(c["table_id"])))
                for kind, amount in c["reserved"].items():
                    self.stock[kind] -= amount
                c["reserved"], c["order_status"] = {}, "assigned"
                s.update(state="cooking", dish={"order_id": c["order_id"], "dish_id": c["dish_id"]},
                    cook_ticks_left=round(self.menu[c["dish_id"]]["cook_s"] * self.hz), ready_ticks=0)
                events.append(("cook_started", dict(stove_id=s["id"], **s["dish"])))
        elif self.hand is not None:
            c = next((c for c in self.customers if c["table_id"] == target["id"] and c["order_id"] == self.hand["order_id"] and c["dish_id"] == self.hand["dish_id"] and c["state"] == "waiting"), None)
            if c is None:
                return
            price = self.menu[c["dish_id"]]["price"]
            tip = math.floor(price * self.t["tip_rate"]) if c["patience_ticks_left"] >= self.t["patience_s"] * self.hz * self.t["tip_min_patience_ratio"] else 0
            c.update(state="eating", price=price, tip=tip, eat_ticks_left=round(self.t["eat_s"] * self.hz))
            self.hand = None
            self.served_count += 1
            events.append(("served", {"customer_id": c["id"], "table_id": c["table_id"], "order_id": c["order_id"], "dish_id": c["dish_id"], "price": price, "tip": tip}))

    def _move(self, inp):
        speed = self.t["walk_speed"]
        self.vel = ramp_velocity(self, tuple(m * speed for m in inp.move), int(self.t["ramp_max_ticks"]))
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / self.hz
            lo, hi = self.t["bounds"][axis]
            if self.pos[i] <= lo:
                self.pos[i], self.vel[i] = lo, max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i], self.vel[i] = hi, min(0.0, self.vel[i])
