"""Kiểm kho v1.1 (gồm hai id mới), giữ schema v1.0."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chonoi.errors import BadInput
from chonoi.inventory import read_inventory


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate a v1.1 inventory without changing it")
    parser.add_argument("path", nargs="?", type=Path,
                        default=ROOT / "docs/contracts/inventory.sample.json")
    args = parser.parse_args(argv)
    try:
        items = read_inventory(str(args.path))
    except BadInput as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"valid": True, "items": items}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
