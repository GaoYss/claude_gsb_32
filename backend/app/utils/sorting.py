"""列表排序参数解析。"""

from sqlalchemy import asc, desc


def parse_sort(args, allowed, default):
    """allowed 形如 {"area_sqm": GreenSpace.area_sqm}，非法字段回退到 default。"""

    field = (args.get("sort") or "").strip()
    column = allowed.get(field)
    if column is None:
        return default
    direction = (args.get("order") or "desc").strip().lower()
    return asc(column) if direction == "asc" else desc(column)
