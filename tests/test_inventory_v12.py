"""Kiểm schema file kho cá thể được quy định trong Ticket-03."""

from pathlib import Path
import unittest

from chonoi.errors import BadInput
from chonoi.inventory import read_inventory, write_inventory
from helpers import Workdir, write_json


class InventoryV12(unittest.TestCase):
    def test_reads_each_individual_including_spoiled_goods(self):
        items = [
            {"id": "I7", "kind": "ca_keo", "fresh": 0},
            {"id": "I2", "kind": "ca_loc", "fresh": 30},
            {"id": "market-fish", "kind": "ca_linh", "fresh": 100},
        ]
        with Workdir() as work:
            path = write_json(work.path("inventory.json"), {"items": items})
            self.assertEqual(read_inventory(path, contract_version="1.2"), items)
            with self.assertRaises(BadInput):
                read_inventory(path, contract_version="1.1")

    def test_rejects_incompatible_or_malformed_inventory(self):
        fish = {"id": "I1", "kind": "ca_loc", "fresh": 97.5}
        invalid = [
            {"items": {"ca_loc": 1}},
            {"items": [], "extra": None},
            {"items": [fish, dict(fish, kind="ca_linh")]},
            {"items": [dict(fish, extra=True)]},
            {"items": [{"id": "I1", "kind": "ca_loc"}]},
            {"items": [None]},
            *({"items": [dict(fish, id=ident)]} for ident in ("", 1, None)),
            *({"items": [dict(fish, kind=kind)]} for kind in ("unknown", [], None)),
            *({"items": [dict(fish, fresh=fresh)]} for fresh in
              (-0.01, 101, float("nan"), float("inf"), True, "30", None, 10**400)),
        ]
        with Workdir() as work:
            for document in invalid:
                with self.subTest(document=document):
                    path = write_json(work.path("inventory.json"), document)
                    with self.assertRaises(BadInput):
                        read_inventory(path, contract_version="1.2")

    def test_writes_numeric_id_order_with_full_freshness_precision(self):
        items = [
            {"id": "I10", "kind": "ca_loc", "fresh": 29.999999999999996},
            {"id": "I2", "kind": "ca_loc", "fresh": 30.000000000000004},
        ]
        with Workdir() as work:
            path_a = work.path("a.json")
            path_b = work.path("b.json")
            write_inventory(path_a, items, contract_version="1.2")
            write_inventory(path_b, list(reversed(items)), contract_version="1.2")
            self.assertEqual(Path(path_a).read_bytes(), Path(path_b).read_bytes())
            self.assertEqual(read_inventory(path_a, contract_version="1.2"), list(reversed(items)))

    def test_empty_and_invalid_write(self):
        with Workdir() as work:
            destination = Path(work.path("inventory.json"))
            write_inventory(destination, [], contract_version="1.2")
            self.assertEqual(destination.read_bytes(), b'{"items":[]}\n')
            with self.assertRaises(BadInput):
                write_inventory(destination, {"ca_loc": 1}, contract_version="1.2")
            self.assertEqual(destination.read_bytes(), b'{"items":[]}\n')

    def test_existing_count_file_selects_ingredient_list_by_version(self):
        with Workdir() as work:
            path = write_json(work.path("inventory.json"), {"items": {"ca_loc": 0, "ca_keo": 1}})
            self.assertEqual(read_inventory(path, contract_version="1.1"), {"ca_keo": 1})
            with self.assertRaises(BadInput):
                read_inventory(path, contract_version="1.0")
