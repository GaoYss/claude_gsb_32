"""业务编号生成。

编号规则：

    绿地台账  GS-2026-0001      按年递增
    养护任务  MT-20260913-001   按日递增
    养护记录  MR-20260913-001   按日递增
    绿植更换  PR-20260913-001   按日递增

同一时刻并发创建时可能产生编号冲突，由 BaseService 捕获唯一约束异常后重试。
"""

from datetime import date

from ..extensions import db


def next_code(model, column, prefix, width=4):
    """在 prefix 范围内取最大序号 +1。"""

    rows = db.session.query(column).filter(column.like(f"{prefix}%")).all()
    max_seq = 0
    for (value,) in rows:
        suffix = (value or "")[len(prefix):]
        if suffix.isdigit():
            max_seq = max(max_seq, int(suffix))
    return f"{prefix}{max_seq + 1:0{width}d}"


def year_prefix(code, day=None):
    day = day or date.today()
    return f"{code}-{day:%Y}-"


def daily_prefix(code, day=None):
    day = day or date.today()
    return f"{code}-{day:%Y%m%d}-"
