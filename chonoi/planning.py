"""Kế hoạch là dữ liệu; dùng chung khi nạp contract và scenario v1.1."""
from .errors import BadInput


def ingredients_for(dishes, menu):
    if not isinstance(dishes, dict) or not dishes:
        raise BadInput("day_plan.dishes phải là map khác rỗng")
    total = {}
    for dish, count in dishes.items():
        if dish not in menu or isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise BadInput("day_plan: món hoặc số suất không hợp lệ")
        for kind, amount in menu[dish]["recipe"].items():
            total[kind] = total.get(kind, 0) + count * amount
    return dict(sorted(total.items()))


def validate_plans(plans, menu, require_all=False):
    if not isinstance(plans, list):
        raise BadInput("day_plan phải là mảng")
    seen, result = set(), []
    for item in plans:
        if not isinstance(item, dict) or set(item) - {"day", "dishes", "ingredients"}:
            raise BadInput("day_plan: trường lạ")
        day = item.get("day")
        if isinstance(day, bool) or not isinstance(day, int) or not 1 <= day <= 5 or day in seen:
            raise BadInput("day_plan.day phải duy nhất trong [1,5]")
        seen.add(day)
        ingredients = ingredients_for(item.get("dishes"), menu)
        if "ingredients" in item:
            from .inventory import validate_items
            if validate_items(item["ingredients"]) != ingredients:
                raise BadInput("day_plan.ingredients khác tổng công thức")
        result.append({"day": day, "dishes": dict(sorted(item["dishes"].items())), "ingredients": ingredients})
    if require_all and seen != set(range(1, 6)):
        raise BadInput("preset cần kế hoạch đủ 5 ngày")
    return sorted(result, key=lambda item: item["day"])
