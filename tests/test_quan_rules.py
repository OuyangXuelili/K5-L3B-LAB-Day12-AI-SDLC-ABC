"""Kiểm hành vi quán theo Ticket-02 mục 1.3; không sửa luật để chiều test."""
import copy
import unittest

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim


def press(*buttons):
    return InputState((0, 0), {}, set(buttons))


def customer(ident="C1", table="T1", dish="ca_loc_nuong_trui", **kw):
    return dict(id=ident, table_id=table, dish_id=dish, **kw)


class QuanRules(unittest.TestCase):
    def setUp(self):
        self.t = copy.deepcopy(load_contract()["tuning"])

    def sim(self, **kw):
        return QuanSim(self.t, kw, Streams(7), IdAllocator())

    def test_reservation_prevents_double_booking_without_spending_stock(self):
        s = self.sim(stock={"ca_loc": 1})
        for _ in range(1020):
            s.step(press())
        self.assertEqual(len(s.customers), 1)
        self.assertEqual(s.stock, {"ca_loc": 1})
        self.assertEqual(s.available_stock(), {"ca_loc": 0})

    def test_arrival_schedule_and_smallest_free_table(self):
        s = self.sim(stock={"ca_loc": 10})
        for _ in range(119):
            self.assertEqual(s.step(press()), [])
        self.assertEqual(s.step(press())[0][0], "customer_arrived")
        for _ in range(900):
            s.step(press())
        self.assertEqual([c["table_id"] for c in s.customers], ["T1", "T2"])

    def test_cook_ready_pick_serve_pay_with_tip(self):
        s = self.sim(stock={"ca_loc": 1}, customers=[customer()], random_customers=False, player={"pos": [2, 8]})
        self.assertEqual(s.step(press("interact"))[0][0], "cook_started")
        self.assertEqual(s.stock["ca_loc"], 0)
        for _ in range(359):
            self.assertEqual(s.step(press()), [])
        self.assertEqual([e[0] for e in s.step(press("interact"))], ["dish_ready", "dish_picked"])
        s.pos = [9, 2]
        self.assertEqual(s.step(press("interact"))[0][0], "served")
        self.assertEqual(s.money, 0)
        for _ in range(600):
            s.step(press())
        self.assertEqual((s.money, s.earned, s.shift_earned), (72, 72, 72))
        self.assertEqual(s.reputation, 3.2)
        self.assertEqual(s.customers, [])

    def test_tip_boundary_checks_patience_after_tick_decrement(self):
        for patience, tip in ((1801, 12), (1800, 0)):
            c = customer(order_status="assigned", patience_ticks_left=patience)
            s = self.sim(customers=[c], hand={"order_id": "C1", "dish_id": c["dish_id"]}, player={"pos": [9, 2]})
            s.step(press("interact"))
            self.assertEqual(s.customers[0]["tip"], tip)

    def test_oldest_order_then_table_id_wins(self):
        s = self.sim(stock={"ca_loc": 3}, customers=[customer("C1", "T2", order_tick=0), customer("C2", "T1", order_tick=0), customer("C3", "T3", order_tick=1)], player={"pos": [2, 8]})
        s.step(press("interact"))
        self.assertEqual(s.stoves[0]["dish"]["order_id"], "C2")

    def test_target_tie_uses_stove_before_table_and_only_one_action(self):
        self.t["quan"]["tables"][0]["pos"] = [2, 8]
        s = self.sim(stock={"ca_loc": 1}, customers=[customer()], player={"pos": [2, 8]})
        self.assertEqual([e[0] for e in s.step(press("interact"))], ["cook_started"])

    def test_wrong_table_does_not_take_hand(self):
        c = customer(order_status="assigned")
        s = self.sim(customers=[c], hand={"order_id": "C1", "dish_id": c["dish_id"]}, player={"pos": [13, 2]})
        self.assertEqual(s.step(press("interact")), [])
        self.assertIsNotNone(s.hand)

    def test_timeout_releases_reserved_stock_and_clamps_reputation(self):
        s = self.sim(stock={"ca_loc": 1}, customers=[customer(patience_ticks_left=1)], reputation=0.2, random_customers=False)
        self.assertEqual(s.step(press())[0][0], "customer_left")
        self.assertEqual(s.available_stock(), {"ca_loc": 1})
        self.assertEqual(s.reputation, 0)

    def test_timeout_discards_assigned_dish(self):
        c = customer(order_status="assigned", patience_ticks_left=1)
        s = self.sim(customers=[c], hand={"order_id": "C1", "dish_id": c["dish_id"]}, random_customers=False)
        s.step(press())
        self.assertIsNone(s.hand)

    def test_close_pays_eating_and_clears_waiting_without_penalty(self):
        s = self.sim(stock={"ca_loc": 1}, time_left_ticks=1, customers=[customer(patience_ticks_left=1), customer("C2", "T2", state="eating", eat_ticks_left=100, price=60, tip=12)], random_customers=False)
        ev = s.step(press())
        self.assertEqual([e[0] for e in ev], ["customer_left", "paid", "quan_end"])
        self.assertEqual(s.reputation, 3.2)
        self.assertEqual(s.money, 72)
        self.assertEqual(s.step(press()), [])

    def test_invalid_assigned_or_overreserved_fixture_rejected(self):
        for kw in ({"customers": [customer(order_status="assigned")]}, {"stock": {}, "customers": [customer()]}, {"stoves": [{"id": "B1", "state": "ready"}]}):
            with self.assertRaises(BadInput):
                self.sim(**kw)

    def test_new_recipes_and_plan_filter(self):
        s = QuanSim(self.t, {"stock": {"ca_keo": 2}}, Streams(1), IdAllocator(), allowed_dishes={"goi_bong_sung"})
        ev = []
        s._arrive(ev)
        self.assertEqual(ev[0][0], "no_dish")
        s = self.sim(stock={"ca_keo": 2})
        ev = []
        s._arrive(ev)
        self.assertEqual(s.customers[0]["dish_id"], "ca_keo_nuong")
