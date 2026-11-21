"""Vòng tick (Contract B, mô hình tick). KHUNG — thường không cần sửa.

Thứ tự ghi: snapshot tick 0 -> với mỗi bước: sự kiện (theo thứ tự xử lý) rồi snapshot (nếu tới lượt
hoặc buổi kết thúc) -> dòng 'end'. Mỗi tick tối đa một snapshot.

`Session` là API bước tick gọn dùng chung cho headless (`run`) và cửa sổ chơi trực tiếp (`chonoi.live`):
cả hai chạy CÙNG một lớp sim, không nhân đôi logic.
"""

import math

from .ids import IdAllocator
from .inputs import InputPlayer
from .inventory import write_inventory
from .jsonl import JsonlWriter
from .rng import Streams
from .sim.gather import GatherSim
from .sim.quan import QuanSim
from .sim.day import DaySim


def build_sim(mode, tuning, scenario, seed, inventory, days=1):
    streams, ids = Streams(seed), IdAllocator()
    if mode == "day":
        return DaySim(tuning, scenario, streams, ids, days)
    if mode == "gather":
        return GatherSim(tuning, scenario, streams, ids)
    return QuanSim(tuning, scenario, streams, ids, inventory=inventory)


def _common(sim, tick, sim_tick, phase_tick, tuning, state):
    mult = tuning["score"]["reputation_multiplier"]
    return {
        "type": "snapshot", "tick": tick, "sim_tick": sim_tick, "mode": sim.mode, "phase": sim.phase,
        "phase_tick": phase_tick, "state": state, "time_left_ticks": sim.time_left_ticks,
        "money": sim.money, "earned": sim.earned, "reputation": sim.reputation,
        "score": sim.earned + mult * math.floor(sim.reputation),
    }


class Session:
    """Một lượt chơi: dựng sim, bước từng tick, lấy snapshot / dòng end."""

    def __init__(self, mode, tuning, scenario, seed, inventory=None, days=1):
        self.mode = mode
        self.tuning = tuning
        self.sim = build_sim(mode, tuning, scenario, seed, inventory, days)
        self.tick = 0
        self.sim_tick = 0
        self.paused = False

    @property
    def done(self) -> bool:
        return self.sim.done

    def snapshot(self) -> dict:
        state = "finished" if self.sim.done else "paused" if self.paused else "playing"
        s = _common(self.sim, self.tick, self.sim_tick, self.sim.phase_tick if self.mode == "day" else self.sim_tick, self.tuning, state)
        s.update(self.sim.snapshot())
        return s

    def step(self, inp) -> list:
        """Chạy một bước với `inp` (chonoi.inputs.InputState); trả các dòng event (tick = k + 1)."""
        if self.done:
            return []
        events = []
        phase, day = self.sim.phase, getattr(self.sim, "day", None)
        if inp.pressed("pause"):
            self.paused = not self.paused
            events.append({"phase": phase, "name": "paused" if self.paused else "resumed", "data": {}})
        if not self.paused:
            events.extend(self.sim.step(inp))
            self.sim_tick += 1
        self.tick += 1
        rows = []
        for ev in events:
            item = ev if isinstance(ev, dict) else {"phase": phase, "name": ev[0], "data": ev[1]}
            row = {"type": "event", "tick": self.tick, **item}
            if self.mode == "day":
                row.setdefault("day", day)
            rows.append(row)
        return rows

    def initial_rows(self):
        return [{"type": "event", "tick": 0, **ev} for ev in self.sim.initial_events()] if self.mode == "day" else []

    def end_row(self) -> dict:
        sim = self.sim
        score = _common(sim, self.tick, self.tick, self.tick, self.tuning, "")["score"]
        row = {"type": "end", "ticks": self.tick, "sim_tick": self.sim_tick, "mode": sim.mode,
                "state": "finished" if sim.done else "paused" if self.paused else "playing",
                "reason": sim.reason if sim.done else "tick_limit",
                "money": sim.money, "earned": sim.earned, "reputation": sim.reputation, "score": score}
        if self.mode == "day":
            row["days_completed"] = sim.days_completed
        return row

    def write_inventory_if_done(self, inventory_out):
        """File kho: ghi MỘT lần khi có gather_end; chưa kết thúc thì giữ nguyên file đích."""
        if self.mode == "gather" and self.sim.done and inventory_out:
            write_inventory(inventory_out, self.sim.inventory_items())


def run(mode, tuning, scenario, seed, frames, ticks, out_path, snapshot_every, inventory=None, inventory_out=None, days=1):
    from .inputs import BUTTONS_V11
    sess = Session(mode, tuning, scenario, seed, inventory, days)
    player = InputPlayer(frames, BUTTONS_V11)
    w = JsonlWriter(out_path)
    try:
        w.write(sess.snapshot())  # tick 0: sau khi dựng scenario, trước mọi input
        for row in sess.initial_rows():
            w.write(row)
        last_snapped = 0
        while sess.tick < ticks and not sess.done:
            previous_phase = (sess.sim.phase, getattr(sess.sim, "day", None))
            inp = player.advance(sess.tick)  # bước k đọc input có tick == k
            for row in sess.step(inp):
                w.write(row)
            changed_phase = previous_phase != (sess.sim.phase, getattr(sess.sim, "day", None))
            if sess.tick % snapshot_every == 0 or sess.done or changed_phase:
                w.write(sess.snapshot())
                last_snapped = sess.tick
        if last_snapped != sess.tick:
            w.write(sess.snapshot())
        w.write(sess.end_row())
    finally:
        w.close()
    sess.write_inventory_if_done(inventory_out)
    return sess.sim
