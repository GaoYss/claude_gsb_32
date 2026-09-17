"""模型公共定义。"""

from datetime import datetime, timezone

from ..extensions import db


def utcnow():
    """统一使用不带时区的 UTC 时间入库，避免 SQLite 时区处理差异。"""

    return datetime.now(timezone.utc).replace(tzinfo=None)


class TimestampMixin:
    """统一的创建/更新时间。"""

    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)


def amount_column():
    """金额列：PostgreSQL 下为 NUMERIC，SQLite 下以 float 回读。"""

    return db.Numeric(14, 2, asdecimal=False)


def quantity_column():
    """数量列（面积、株数、工时等）。"""

    return db.Numeric(12, 2, asdecimal=False)
