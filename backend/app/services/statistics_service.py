"""统计看板：全部使用聚合查询，不把明细数据搬到前端计算。"""

from datetime import timedelta

from sqlalchemy import func

from ..constants import ENUM_GROUPS
from ..extensions import db
from ..models import GreenSpace, MaintenanceRecord, MaintenanceTask, PlantReplacement
from ..models.maintenance_task import OPEN_STATUSES
from ..utils.dates import today
from ..utils.numbers import to_float


class StatisticsService:
    """看板与各类分布统计。"""

    # ------------------------------------------------------------ 工具
    @staticmethod
    def _month_starts(months):
        cursor = today().replace(day=1)
        starts = []
        for _ in range(max(months, 1)):
            starts.append(cursor)
            cursor = (cursor - timedelta(days=1)).replace(day=1)
        return list(reversed(starts))

    # ------------------------------------------------------------ 总览
    @staticmethod
    def overview():
        current = today()
        month_start = current.replace(day=1)
        year_start = current.replace(month=1, day=1)

        space_total, space_area = db.session.query(
            func.count(GreenSpace.id), func.coalesce(func.sum(GreenSpace.area_sqm), 0)
        ).one()
        space_rows = (
            db.session.query(GreenSpace.status, func.count(GreenSpace.id))
            .group_by(GreenSpace.status)
            .all()
        )
        space_status = {code: 0 for code in ENUM_GROUPS["green_space_status"].values}
        for status, count in space_rows:
            space_status[status] = count

        task_rows = (
            db.session.query(MaintenanceTask.status, func.count(MaintenanceTask.id))
            .group_by(MaintenanceTask.status)
            .all()
        )
        task_status = {code: 0 for code in ENUM_GROUPS["task_status"].values}
        for status, count in task_rows:
            task_status[status] = count
        task_total = sum(task_status.values())

        overdue = (
            db.session.query(func.count(MaintenanceTask.id))
            .filter(MaintenanceTask.status.in_(OPEN_STATUSES), MaintenanceTask.plan_date < current)
            .scalar()
            or 0
        )
        due_soon = (
            db.session.query(func.count(MaintenanceTask.id))
            .filter(
                MaintenanceTask.status.in_(OPEN_STATUSES),
                MaintenanceTask.plan_date >= current,
                MaintenanceTask.plan_date <= current + timedelta(days=7),
            )
            .scalar()
            or 0
        )

        record_total, hours_total = db.session.query(
            func.count(MaintenanceRecord.id),
            func.coalesce(func.sum(MaintenanceRecord.work_hours), 0),
        ).one()
        month_records, month_hours = db.session.query(
            func.count(MaintenanceRecord.id),
            func.coalesce(func.sum(MaintenanceRecord.work_hours), 0),
        ).filter(MaintenanceRecord.record_date >= month_start).one()

        replacement_total, quantity_total, amount_total = db.session.query(
            func.count(PlantReplacement.id),
            func.coalesce(func.sum(PlantReplacement.quantity), 0),
            func.coalesce(func.sum(PlantReplacement.amount), 0),
        ).one()
        month_count, month_quantity, month_amount = db.session.query(
            func.count(PlantReplacement.id),
            func.coalesce(func.sum(PlantReplacement.quantity), 0),
            func.coalesce(func.sum(PlantReplacement.amount), 0),
        ).filter(PlantReplacement.replace_date >= month_start).one()
        _, year_quantity, year_amount = db.session.query(
            func.count(PlantReplacement.id),
            func.coalesce(func.sum(PlantReplacement.quantity), 0),
            func.coalesce(func.sum(PlantReplacement.amount), 0),
        ).filter(PlantReplacement.replace_date >= year_start).one()

        completed = task_status.get("completed", 0)
        return {
            "generated_at": f"{current:%Y-%m-%d}",
            "green_space": {
                "total": space_total or 0,
                "total_area": to_float(space_area) or 0,
                "by_status": space_status,
            },
            "task": {
                "total": task_total,
                "by_status": task_status,
                "open_count": task_status.get("pending", 0) + task_status.get("in_progress", 0),
                "overdue_count": overdue,
                "due_soon_count": due_soon,
                "completion_rate": round(completed / task_total * 100, 1) if task_total else 0.0,
            },
            "record": {
                "total": record_total or 0,
                "total_work_hours": to_float(hours_total) or 0,
                "month_count": month_records or 0,
                "month_work_hours": to_float(month_hours) or 0,
            },
            "replacement": {
                "total": replacement_total or 0,
                "total_quantity": to_float(quantity_total) or 0,
                "total_amount": to_float(amount_total) or 0,
                "month_count": month_count or 0,
                "month_quantity": to_float(month_quantity) or 0,
                "month_amount": to_float(month_amount) or 0,
                "year_quantity": to_float(year_quantity) or 0,
                "year_amount": to_float(year_amount) or 0,
            },
        }

    # ------------------------------------------------------------ 分布
    @staticmethod
    def distributions():
        type_rows = (
            db.session.query(
                GreenSpace.green_type,
                func.count(GreenSpace.id),
                func.coalesce(func.sum(GreenSpace.area_sqm), 0),
            )
            .group_by(GreenSpace.green_type)
            .all()
        )
        grade_rows = (
            db.session.query(
                GreenSpace.maintenance_grade,
                func.count(GreenSpace.id),
                func.coalesce(func.sum(GreenSpace.area_sqm), 0),
            )
            .group_by(GreenSpace.maintenance_grade)
            .all()
        )
        district_rows = (
            db.session.query(
                GreenSpace.district,
                func.count(GreenSpace.id),
                func.coalesce(func.sum(GreenSpace.area_sqm), 0),
            )
            .group_by(GreenSpace.district)
            .order_by(func.count(GreenSpace.id).desc())
            .limit(10)
            .all()
        )
        task_type_rows = (
            db.session.query(MaintenanceTask.task_type, func.count(MaintenanceTask.id))
            .group_by(MaintenanceTask.task_type)
            .all()
        )
        priority_rows = (
            db.session.query(MaintenanceTask.priority, func.count(MaintenanceTask.id))
            .group_by(MaintenanceTask.priority)
            .all()
        )
        category_rows = (
            db.session.query(
                PlantReplacement.plant_category,
                func.count(PlantReplacement.id),
                func.coalesce(func.sum(PlantReplacement.quantity), 0),
                func.coalesce(func.sum(PlantReplacement.amount), 0),
            )
            .group_by(PlantReplacement.plant_category)
            .all()
        )
        reason_rows = (
            db.session.query(
                PlantReplacement.reason,
                func.count(PlantReplacement.id),
                func.coalesce(func.sum(PlantReplacement.quantity), 0),
            )
            .group_by(PlantReplacement.reason)
            .all()
        )

        def _with_area(group_key, rows):
            return [
                {
                    "value": value,
                    "label": ENUM_GROUPS[group_key].label(value),
                    "count": count,
                    "area_sqm": to_float(area) or 0,
                }
                for value, count, area in rows
            ]

        def _simple(group_key, rows):
            return [
                {"value": value, "label": ENUM_GROUPS[group_key].label(value), "count": count}
                for value, count in rows
            ]

        return {
            "green_space_by_type": _with_area("green_space_type", type_rows),
            "green_space_by_grade": _with_area("maintenance_grade", grade_rows),
            "green_space_by_district": [
                {
                    "value": district,
                    "label": district,
                    "count": count,
                    "area_sqm": to_float(area) or 0,
                }
                for district, count, area in district_rows
            ],
            "task_by_type": _simple("task_type", task_type_rows),
            "task_by_priority": _simple("task_priority", priority_rows),
            "replacement_by_category": [
                {
                    "value": value,
                    "label": ENUM_GROUPS["plant_category"].label(value),
                    "count": count,
                    "quantity": to_float(quantity) or 0,
                    "amount": to_float(amount) or 0,
                }
                for value, count, quantity, amount in category_rows
            ],
            "replacement_by_reason": [
                {
                    "value": value,
                    "label": ENUM_GROUPS["replacement_reason"].label(value),
                    "count": count,
                    "quantity": to_float(quantity) or 0,
                }
                for value, count, quantity in reason_rows
            ],
        }

    # ------------------------------------------------------------ 趋势
    @staticmethod
    def trends(months=6):
        """近 N 个月的养护记录与绿植更换趋势（按自然月聚合）。"""

        starts = StatisticsService._month_starts(months)
        buckets = {}
        for start in starts:
            buckets[f"{start:%Y-%m}"] = {
                "month": f"{start:%Y-%m}",
                "record_count": 0,
                "work_hours": 0.0,
                "replacement_count": 0,
                "replacement_quantity": 0.0,
                "replacement_amount": 0.0,
            }

        start = starts[0]
        record_rows = (
            db.session.query(MaintenanceRecord.record_date, MaintenanceRecord.work_hours)
            .filter(MaintenanceRecord.record_date >= start)
            .all()
        )
        for record_date, work_hours in record_rows:
            bucket = buckets.get(f"{record_date:%Y-%m}")
            if bucket is None:
                continue
            bucket["record_count"] += 1
            bucket["work_hours"] = round(bucket["work_hours"] + float(work_hours or 0), 2)

        replacement_rows = (
            db.session.query(
                PlantReplacement.replace_date,
                PlantReplacement.quantity,
                PlantReplacement.amount,
            )
            .filter(PlantReplacement.replace_date >= start)
            .all()
        )
        for replace_date, quantity, amount in replacement_rows:
            bucket = buckets.get(f"{replace_date:%Y-%m}")
            if bucket is None:
                continue
            bucket["replacement_count"] += 1
            bucket["replacement_quantity"] = round(
                bucket["replacement_quantity"] + float(quantity or 0), 2
            )
            bucket["replacement_amount"] = round(
                bucket["replacement_amount"] + float(amount or 0), 2
            )

        return [buckets[f"{start:%Y-%m}"] for start in starts]

    # ------------------------------------------------------------ 榜单与提醒
    @staticmethod
    def green_space_ranking(limit=5):
        replacement_quantity = (
            db.select(func.coalesce(func.sum(PlantReplacement.quantity), 0))
            .where(PlantReplacement.green_space_id == GreenSpace.id)
            .correlate(GreenSpace)
            .scalar_subquery()
        )
        rows = (
            db.session.query(
                GreenSpace.id,
                GreenSpace.code,
                GreenSpace.name,
                GreenSpace.district,
                GreenSpace.area_sqm,
                func.count(MaintenanceRecord.id),
                func.coalesce(func.sum(MaintenanceRecord.work_hours), 0),
                replacement_quantity,
            )
            .join(MaintenanceRecord, MaintenanceRecord.green_space_id == GreenSpace.id)
            .group_by(GreenSpace.id, GreenSpace.code, GreenSpace.name, GreenSpace.district,
                      GreenSpace.area_sqm)
            .order_by(func.count(MaintenanceRecord.id).desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "green_space_id": space_id,
                "code": code,
                "name": name,
                "district": district,
                "area_sqm": to_float(area) or 0,
                "record_count": record_count,
                "total_work_hours": to_float(hours) or 0,
                "replacement_quantity": to_float(quantity) or 0,
            }
            for space_id, code, name, district, area, record_count, hours, quantity in rows
        ]

    @staticmethod
    def overdue_tasks(limit=10):
        tasks = (
            db.session.query(MaintenanceTask)
            .filter(
                MaintenanceTask.status.in_(OPEN_STATUSES),
                MaintenanceTask.plan_date < today(),
            )
            .order_by(MaintenanceTask.plan_date.asc())
            .limit(limit)
            .all()
        )
        return [task.to_dict() for task in tasks]

    @staticmethod
    def upcoming_tasks(limit=10):
        tasks = (
            db.session.query(MaintenanceTask)
            .filter(
                MaintenanceTask.status.in_(OPEN_STATUSES),
                MaintenanceTask.plan_date >= today(),
            )
            .order_by(MaintenanceTask.plan_date.asc())
            .limit(limit)
            .all()
        )
        return [task.to_dict() for task in tasks]

    @staticmethod
    def recent_activity(limit=6):
        records = (
            db.session.query(MaintenanceRecord)
            .order_by(MaintenanceRecord.record_date.desc(), MaintenanceRecord.id.desc())
            .limit(limit)
            .all()
        )
        replacements = (
            db.session.query(PlantReplacement)
            .order_by(PlantReplacement.replace_date.desc(), PlantReplacement.id.desc())
            .limit(limit)
            .all()
        )
        return {
            "records": [item.to_dict() for item in records],
            "replacements": [item.to_dict() for item in replacements],
        }

    # ------------------------------------------------------------ 汇总入口
    @staticmethod
    def dashboard(months=6):
        """看板一次性取数，减少前端并发请求。"""

        return {
            "overview": StatisticsService.overview(),
            "distributions": StatisticsService.distributions(),
            "trends": StatisticsService.trends(months),
            "ranking": StatisticsService.green_space_ranking(),
            "overdue_tasks": StatisticsService.overdue_tasks(),
            "upcoming_tasks": StatisticsService.upcoming_tasks(),
            "recent_activity": StatisticsService.recent_activity(),
        }
