"""系统字典与健康检查接口。"""

from flask import Blueprint

from ..constants import all_enums
from ..extensions import db
from ..utils.responses import ok
from sqlalchemy import text

bp = Blueprint("meta", __name__)


@bp.get("/meta/enums")
def enums():
    """下发全部业务字典，前端下拉统一从这里初始化。"""

    return ok({"enums": all_enums()})


@bp.get("/meta/health")
def health():
    """健康检查：同时探测数据库连通性，供容器编排使用。"""

    try:
        db.session.execute(text("SELECT 1"))
        database = "up"
    except Exception as exc:  # pragma: no cover - 仅在数据库不可用时触发
        database = f"down: {exc}"
    return ok({"status": "ok" if database == "up" else "degraded", "database": database})
