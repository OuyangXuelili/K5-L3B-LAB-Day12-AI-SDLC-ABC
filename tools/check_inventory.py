"""Kiểm file kho theo phiên bản Test Contract."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.inventory import read_inventory


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate an inventory without changing it")
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--contract-version", choices=("1.0", "1.1", "1.2"))
    args = parser.parse_args(argv)
    try:
        version = args.contract_version or load_contract()["contract_version"]
        samples = {"1.0": "inventory.sample.json", "1.1": "inventory.phase2.sample.json",
                   "1.2": "inventory.phase3.sample.json"}
        path = args.path or ROOT / "docs" / "contracts" / samples[version]
        items = read_inventory(path, contract_version=version)
    except BadInput as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"valid": True, "items": items}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
