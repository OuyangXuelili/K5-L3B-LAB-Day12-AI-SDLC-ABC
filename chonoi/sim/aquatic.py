"""Cá bơi/sinh và cá sấu: dữ liệu v1.1, RNG chỉ qua Streams."""
import copy
import math

from ..ids import sort_by_id


def seed_fish(sim, count):
    sim.fish = []
    for _ in range(count):
        spawn_fish(sim)


def spawn_fish(sim):
    t = sim.t
    choices = {}
    for kind in sorted(t["fish_weights"]):
        points = [[x, d] for x in t["fish_spawn_x"] for d in t["fish_spawn_depths"][kind]]
        choices[kind] = [p for p in points if all(math.dist(p, f["pos"]) > t["fish_spawn_clearance"] for f in sim.fish)]
    kinds = [k for k in sorted(choices) if choices[k]]
    if not kinds:
        return None
    rng = sim.rng.get("fish_spawn")
    kind = rng.choices(kinds, weights=[t["fish_weights"][k] for k in kinds], k=1)[0]
    fish = {"id": sim.ids.new("F"), "kind": kind, "pos": list(rng.choice(choices[kind])),
            "heading_deg": rng.uniform(0, 360), "age_ticks": 0}
    sim.fish.append(fish)
    return fish


def swim_and_spawn(sim, events):
    if not sim.random_fish or "fish_speed" not in sim.t:
        return
    t = sim.t
    for f in sort_by_id(sim.fish):
        f["age_ticks"] += 1
        if f["age_ticks"] % t["fish_turn_ticks"] == 0:
            f["heading_deg"] = sim.rng.get("fish_turn").uniform(0, 360)
        angle = math.radians(f["heading_deg"])
        direction = [math.cos(angle), math.sin(angle)]
        for i, band in enumerate((t["fish_x"], t["fish_depths"][f["kind"]])):
            lo, hi = band
            v = f["pos"][i] + direction[i] * t["fish_speed"] / sim.tick_hz
            while v < lo or v > hi:
                v = 2 * lo - v if v < lo else 2 * hi - v
                direction[i] *= -1
            if (v == lo and direction[i] < 0) or (v == hi and direction[i] > 0):
                direction[i] *= -1
            f["pos"][i] = v
        f["heading_deg"] = math.degrees(math.atan2(direction[1], direction[0])) % 360
    if sim.phase_tick % t["fish_spawn_ticks"] == 0 and len(sim.fish) < t["fish_max"]:
        fish = spawn_fish(sim)
        if fish:
            events.append(("fish_spawned", {k: copy.deepcopy(fish[k]) for k in ("id", "kind", "pos")}))


def init_monsters(sim, scenario):
    data = sim.t.get("monsters", {})
    sources = scenario.get("monsters", [m for m in data.get("spawns", []) if m["from_day"] <= scenario.get("_day", 1)])
    sim.monsters = []
    for source in sources:
        m = copy.deepcopy(source)
        m.pop("from_day", None)
        m.setdefault("state", "patrol")
        m.setdefault("target_idx", 1)
        m.setdefault("state_ticks_left", 0)
        m.setdefault("recoil_dir", None)
        sim.monsters.append(m)
        sim.ids.reserve(m["id"])
    sim.invuln_ticks = scenario.get("player", {}).get("invuln_ticks", 0)


def _direction(origin, target):
    distance = math.dist(origin, target)
    return [(target[i] - origin[i]) / distance for i in range(2)] if distance else [1.0, 0.0]


def update_monsters(sim, events):
    data = sim.t.get("monsters")
    if not data:
        return
    eligible = []
    for m in sort_by_id(sim.monsters):
        species = data["species"][m["kind"]]
        if m["state"] == "recoil":
            for i in range(2):
                m["pos"][i] += m["recoil_dir"][i] * species["recoil_dist"] / species["recoil_ticks"]
            m["state_ticks_left"] -= 1
            if m["state_ticks_left"] == 0:
                m.update(state="patrol", recoil_dir=None)
        else:
            distance = math.dist(sim.pos, m["pos"])
            deep = sim.pos[1] >= species["depths"][0]
            if m["state"] == "patrol" and deep and distance <= species["detect_radius"]:
                m["state"] = "chase"
            elif m["state"] == "chase" and (not deep or distance > species["exit_radius"]):
                m["state"] = "patrol"
            target = sim.pos if m["state"] == "chase" else m["waypoints"][m["target_idx"]]
            direction = _direction(m["pos"], target)
            step = min(math.dist(m["pos"], target), species[m["state"] + "_speed"] / sim.tick_hz)
            m["pos"] = [m["pos"][i] + direction[i] * step for i in range(2)]
            if m["state"] == "patrol" and math.dist(m["pos"], target) < 1e-10:
                m["target_idx"] = 1 - m["target_idx"]
            if deep and math.dist(sim.pos, m["pos"]) <= species["hit_radius"]:
                eligible.append(m)
        for i, bounds in enumerate((sim.t["bounds"]["x"], species["depths"])):
            m["pos"][i] = max(bounds[0], min(bounds[1], m["pos"][i]))
    if eligible and sim.invuln_ticks == 0:
        m = min(eligible, key=lambda e: math.dist(sim.pos, e["pos"]))
        species = data["species"][m["kind"]]
        sim.hp = max(0, sim.hp - 1)
        lost = [sim.hold.pop() for _ in range(math.floor(len(sim.hold) * data["loss_ratio"]))]
        sim.invuln_ticks = data["invuln_ticks"]
        m.update(state="recoil", state_ticks_left=species["recoil_ticks"], recoil_dir=_direction(sim.pos, m["pos"]))
        events.append(("monster_hit", {"monster_id": m["id"], "hp": sim.hp, "lost": lost, "pos": list(sim.pos)}))
