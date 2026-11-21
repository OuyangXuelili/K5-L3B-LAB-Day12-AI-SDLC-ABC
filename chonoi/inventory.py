"""Đọc và ghi file kho theo phiên bản Test Contract.

Bản 1.0–1.1 lưu số lượng mỗi loại, bản 1.2 lưu từng cá thể với độ tươi.
Ghi qua file tạm cùng thư mục rồi thay thế nguyên tử.
"""

import json
import os
import tempfile

from .errors import BadInput
from .ids import sort_by_id

KINDS_P1 = ("ca_loc", "ca_linh", "bong_dien_dien", "bong_sung")
KINDS_P2 = (*KINDS_P1, "ca_keo", "keo_neo")


def validate_items(items, kinds=KINDS_P2):
    if not isinstance(items, dict):
        raise BadInput("items phải là object")
    out = {}
    for k, v in items.items():
        if k not in kinds:
            raise BadInput(f"nguyên liệu lạ: {k}")
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise BadInput(f"số lượng không hợp lệ cho {k}: {v!r}")
        if v > 0:
            out[k] = v
    return out


def validate_individuals(items, kinds=KINDS_P2):
    """Kiểm và sao chép mảng cá thể v1.2, giữ thứ tự nguồn."""
    if not isinstance(items, list):
        raise BadInput("items v1.2 phải là mảng cá thể")

    validated = []
    seen = set()
    for item in items:
        if not isinstance(item, dict) or set(item) != {"id", "kind", "fresh"}:
            raise BadInput("cá thể phải có đúng ba khóa id, kind và fresh")
        ident, kind, fresh = item["id"], item["kind"], item["fresh"]
        if not isinstance(ident, str) or not ident or ident in seen:
            raise BadInput(f"id cá thể phải là chuỗi khác rỗng và duy nhất: {ident!r}")
        if not isinstance(kind, str) or kind not in kinds:
            raise BadInput(f"nguyên liệu lạ: {kind}")
        if isinstance(fresh, bool) or not isinstance(fresh, (int, float)) or not 0 <= fresh <= 100:
            raise BadInput(f"độ tươi của {ident} phải là số hữu hạn trong [0, 100]")
        seen.add(ident)
        validated.append({"id": ident, "kind": kind, "fresh": fresh})
    return validated


def read_inventory(path: str, kinds=None, *, contract_version="1.1") -> dict | list:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được file kho {path}: {e}")
    if not isinstance(data, dict) or set(data.keys()) != {"items"}:
        raise BadInput("file kho chỉ được có khóa gốc 'items'")
    if kinds is None:
        kinds = KINDS_P1 if contract_version == "1.0" else KINDS_P2
    if contract_version in ("1.2", "1.3"):
        return validate_individuals(data["items"], kinds)
    if contract_version in ("1.0", "1.1"):
        return validate_items(data["items"], kinds)
    raise BadInput(f"phiên bản kho chưa hỗ trợ: {contract_version!r}")


def hold_to_items(hold: list) -> dict:
    """Khoang (mảng id theo thứ tự nhặt) -> object đếm, sắp theo id nguyên liệu."""
    counts = {}
    for k in hold:
        counts[k] = counts.get(k, 0) + 1
    return {k: counts[k] for k in sorted(counts)}


def write_inventory(path: str, items: dict | list, *, contract_version="1.1", kinds=KINDS_P2):
    if contract_version in ("1.2", "1.3"):
        items = sort_by_id(validate_individuals(items, kinds))
    elif contract_version in ("1.0", "1.1"):
        items = {k: items[k] for k in sorted(items) if items[k] > 0}
    else:
        raise BadInput(f"phiên bản kho chưa hỗ trợ: {contract_version!r}")
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".inv-", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"items": items}, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
