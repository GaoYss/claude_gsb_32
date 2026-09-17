"""数值转换辅助：数据库 Numeric 返回 Decimal，需转成前端可用的 float。"""

from decimal import Decimal, InvalidOperation


def to_float(value, digits=2):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return round(float(value), digits)
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None


def to_decimal(value, field_label="数值"):
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_label}必须是数字") from exc
