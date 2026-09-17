"""养护任务业务逻辑。"""

from sqlalchemy import func, or_

from ..constants import ENUM_GROUPS
from ..errors import ConflictError, ValidationError
from ..extensions import db
from ..models import GreenSpace, MaintenanceRecord, MaintenanceTask, PlantReplacement
from ..models.maintenance_task import OPEN_STATUSES
from ..models.mixins import utcnow
from ..utils.dates import format_date, today
from ..utils.numbers import to_float
from ..utils.sorting import parse_sort
from .base_service import BaseService
from .code_generator import daily_prefix


class MaintenanceTaskService(BaseService):
    """养护任务登记：创建、检索、状态流转与删除保护。"""

    model = MaintenanceTask
    label = "养护任务"
    code_field = "task_no"
    code_width = 3

    SORTABLE = {
        "plan_date": MaintenanceTask.plan_date,
        "task_no": MaintenanceTask.task_no,
        "created_at": MaintenanceTask.created_at,
    }

    @classmethod
    def code_prefix(cls):
        return daily_prefix("MT")

    # ------------------------------------------------------------ 校验
    @classmethod
    def prepare_instance(cls, instance, payload):
        green_space_id = payload.get("green_space_id", instance.green_space_id)
        space = db.session.get(GreenSpace, green_space_id) if green_space_id else None
        if space is None:
            raise ValidationError("登记失败", details={"green_space_id": "所选绿地不存在"})
        if space.status == "archived":
            raise ConflictError(f"绿地「{space.name}」已归档，不能再登记养护任务")

    @classmethod
    def apply_derived(cls, instance):
        """状态与完成时间保持一致：完成即写入完成时间，撤销完成即清空。"""

        if instance.status == "completed":
            if instance.completed_at is None:
                instance.completed_at = utcnow()
        else:
            instance.completed_at = None

    @classmethod
    def _apply_filters(cls, query, filters):
        if filters.get("green_space_id"):
            query = query.filter(MaintenanceTask.green_space_id == filters["green_space_id"])
        if filters.get("status"):
            query = query.filter(MaintenanceTask.status == filters["status"])
        if filters.get("task_type"):
            query = query.filter(MaintenanceTask.task_type == filters["task_type"])
        if filters.get("priority"):
            query = query.filter(MaintenanceTask.priority == filters["priority"])
        if filters.get("date_from"):
            query = query.filter(MaintenanceTask.plan_date >= filters["date_from"])
        if filters.get("date_to"):
            query = query.filter(MaintenanceTask.plan_date <= filters["date_to"])
        if filters.get("overdue"):
            query = query.filter(
                MaintenanceTask.status.in_(OPEN_STATUSES),
                MaintenanceTask.plan_date < today(),
            )
        if filters.get("unplanned"):
            query = query.filter(MaintenanceTask.status == "pending")
        keyword = filters.get("keyword")
        if keyword:
            like = f"%{keyword}%"
            query = query.filter(
                or_(
                    MaintenanceTask.task_no.like(like),
                    MaintenanceTask.title.like(like),
                    MaintenanceTask.executor.like(like),
                    MaintenanceTask.description.like(like),
                )
            )
        return query

    # ------------------------------------------------------------ 查询
    @classmethod
    def list_tasks(cls, filters, args):
        """列表查询：附带每条任务的养护记录进度，便于一眼看出执行情况。"""

        record_count = (
            db.select(func.count(MaintenanceRecord.id))
            .where(MaintenanceRecord.task_id == MaintenanceTask.id)
            .correlate(MaintenanceTask)
            .scalar_subquery()
        )
        qualified_count = (
            db.select(func.count(MaintenanceRecord.id))
            .where(
                MaintenanceRecord.task_id == MaintenanceTask.id,
                MaintenanceRecord.quality_result == "qualified",
            )
            .correlate(MaintenanceTask)
            .scalar_subquery()
        )
        query = db.session.query(
            MaintenanceTask,
            record_count.label("record_count"),
            qualified_count.label("qualified_count"),
        )
        query = cls._apply_filters(query, filters)
        query = query.order_by(parse_sort(args, cls.SORTABLE, MaintenanceTask.plan_date.desc()))
        return query

    @classmethod
    def serialize_row(cls, row):
        task, record_count, qualified_count = row
        data = task.to_dict()
        data["progress"] = {
            "record_count": record_count or 0,
            "qualified_count": qualified_count or 0,
        }
        return data

    @classmethod
    def detail(cls, obj_id):
        task = cls.get(obj_id)
        records = (
            db.session.query(MaintenanceRecord)
            .filter(MaintenanceRecord.task_id == task.id)
            .order_by(MaintenanceRecord.record_date.desc(), MaintenanceRecord.id.desc())
            .all()
        )
        replacement_stats = db.session.query(
            func.count(PlantReplacement.id),
            func.coalesce(func.sum(PlantReplacement.quantity), 0),
            func.coalesce(func.sum(PlantReplacement.amount), 0),
        ).join(MaintenanceRecord, PlantReplacement.maintenance_record_id == MaintenanceRecord.id) \
            .filter(MaintenanceRecord.task_id == task.id).one()

        data = task.to_dict(detail=True)
        data["records"] = [item.to_dict() for item in records]
        data["progress"] = {
            "record_count": len(records),
            "qualified_count": sum(1 for item in records if item.quality_result == "qualified"),
            "unqualified_count": sum(1 for item in records if item.quality_result == "unqualified"),
            "total_work_hours": to_float(sum((item.work_hours or 0) for item in records)) or 0,
            "replacement_count": replacement_stats[0] or 0,
            "replacement_quantity": to_float(replacement_stats[1]) or 0,
            "replacement_amount": to_float(replacement_stats[2]) or 0,
            "last_record_date": format_date(records[0].record_date) if records else None,
        }
        return data

    # ------------------------------------------------------------ 状态流转
    @classmethod
    def change_status(cls, obj_id, payload):
        """手动流转任务状态。

        规则：存在不合格养护记录时不允许直接标记完成，需先整改；
        标记完成会写入完成时间，撤销完成则清空完成时间。
        """

        task = cls.get(obj_id)
        status = payload["status"]
        if payload.get("description") is not None:
            task.description = payload["description"]

        if status == "completed":
            unqualified = (
                db.session.query(func.count(MaintenanceRecord.id))
                .filter(
                    MaintenanceRecord.task_id == task.id,
                    MaintenanceRecord.quality_result == "unqualified",
                )
                .scalar()
                or 0
            )
            if unqualified:
                raise ConflictError(
                    f"该任务存在 {unqualified} 条不合格养护记录，请整改复检合格后再标记完成"
                )
            task.completed_at = task.completed_at or utcnow()
        else:
            task.completed_at = None

        task.status = status
        db.session.commit()
        return task

    # ------------------------------------------------------------ 删除
    @classmethod
    def delete(cls, obj_id, force=False):
        task = cls.get(obj_id)
        record_count = (
            db.session.query(func.count(MaintenanceRecord.id))
            .filter(MaintenanceRecord.task_id == task.id)
            .scalar()
            or 0
        )
        if record_count and not force:
            raise ConflictError(
                f"该任务已登记 {record_count} 条养护记录，请确认后再删除",
                details={"maintenance_record": record_count},
            )
        if record_count:
            # 强制删除时保留养护记录，仅解除任务关联，避免历史数据丢失
            db.session.query(MaintenanceRecord).filter(
                MaintenanceRecord.task_id == task.id
            ).update({MaintenanceRecord.task_id: None}, synchronize_session=False)
        db.session.delete(task)
        db.session.commit()
        return {"detached_records": record_count}

    @classmethod
    def status_summary(cls):
        rows = (
            db.session.query(MaintenanceTask.status, func.count(MaintenanceTask.id))
            .group_by(MaintenanceTask.status)
            .all()
        )
        summary = {code: 0 for code in ENUM_GROUPS["task_status"].values}
        for status, count in rows:
            summary[status] = count
        return summary
