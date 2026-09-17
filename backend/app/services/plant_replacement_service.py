"""绿植更换记录业务逻辑。"""

from decimal import Decimal

from sqlalchemy import func, or_

from ..constants import ENUM_GROUPS
from ..errors import ValidationError
from ..extensions import db
from ..models import GreenSpace, MaintenanceRecord, PlantReplacement
from ..utils.numbers import to_float
from ..utils.sorting import parse_sort
from .base_service import BaseService
from .code_generator import daily_prefix


class PlantReplacementService(BaseService):
    """绿植更换记录：登记更换明细并自动核算金额。"""

    model = PlantReplacement
    label = "绿植更换记录"
    code_field = "replacement_no"
    code_width = 3

    SORTABLE = {
        "replace_date": PlantReplacement.replace_date,
        "quantity": PlantReplacement.quantity,
        "amount": PlantReplacement.amount,
        "created_at": PlantReplacement.created_at,
    }

    @classmethod
    def code_prefix(cls):
        return daily_prefix("PR")

    # ------------------------------------------------------------ 校验与派生
    @classmethod
    def prepare_instance(cls, instance, payload):
        green_space_id = payload.get("green_space_id", instance.green_space_id)
        space = db.session.get(GreenSpace, green_space_id) if green_space_id else None
        if space is None:
            raise ValidationError("登记失败", details={"green_space_id": "所选绿地不存在"})

        record_id = payload.get("maintenance_record_id", instance.maintenance_record_id)
        if record_id:
            record = db.session.get(MaintenanceRecord, record_id)
            if record is None:
                raise ValidationError(
                    "登记失败", details={"maintenance_record_id": "关联的养护记录不存在"}
                )
            if record.green_space_id != space.id:
                raise ValidationError(
                    "登记失败",
                    details={"maintenance_record_id": "关联的养护记录不属于所选绿地"},
                )

        replace_date = payload.get("replace_date", instance.replace_date)
        if replace_date and space.established_date and replace_date < space.established_date:
            raise ValidationError(
                "登记失败",
                details={"replace_date": f"更换日期不能早于该绿地建成日期 {space.established_date}"},
            )

    @classmethod
    def apply_derived(cls, instance):
        """金额 = 数量 × 单价；未填单价时留空，由前端提示补录。"""

        if instance.unit_price is None:
            instance.amount = None
        else:
            instance.amount = (
                Decimal(str(instance.quantity or 0)) * Decimal(str(instance.unit_price))
            ).quantize(Decimal("0.01"))

    # ------------------------------------------------------------ 查询
    @classmethod
    def _apply_filters(cls, query, filters):
        if filters.get("green_space_id"):
            query = query.filter(PlantReplacement.green_space_id == filters["green_space_id"])
        if filters.get("maintenance_record_id"):
            query = query.filter(
                PlantReplacement.maintenance_record_id == filters["maintenance_record_id"]
            )
        if filters.get("plant_category"):
            query = query.filter(PlantReplacement.plant_category == filters["plant_category"])
        if filters.get("reason"):
            query = query.filter(PlantReplacement.reason == filters["reason"])
        if filters.get("date_from"):
            query = query.filter(PlantReplacement.replace_date >= filters["date_from"])
        if filters.get("date_to"):
            query = query.filter(PlantReplacement.replace_date <= filters["date_to"])
        keyword = filters.get("keyword")
        if keyword:
            like = f"%{keyword}%"
            query = query.filter(
                or_(
                    PlantReplacement.replacement_no.like(like),
                    PlantReplacement.plant_name.like(like),
                    PlantReplacement.spec.like(like),
                    PlantReplacement.supplier.like(like),
                    PlantReplacement.operator.like(like),
                )
            )
        return query

    @classmethod
    def list_replacements(cls, filters, args):
        query = cls._apply_filters(db.session.query(PlantReplacement), filters)
        return query.order_by(
            parse_sort(args, cls.SORTABLE, PlantReplacement.replace_date.desc())
        )

    @classmethod
    def detail(cls, obj_id):
        return cls.get(obj_id).to_dict(detail=True)

    @classmethod
    def summary(cls, filters):
        """更换汇总：按植物类别与更换原因统计数量、金额。"""

        def _group(column, group_key):
            rows = (
                cls._apply_filters(
                    db.session.query(
                        column,
                        func.count(PlantReplacement.id),
                        func.coalesce(func.sum(PlantReplacement.quantity), 0),
                        func.coalesce(func.sum(PlantReplacement.amount), 0),
                    ),
                    filters,
                )
                .group_by(column)
                .all()
            )
            return [
                {
                    "value": value,
                    "label": ENUM_GROUPS[group_key].label(value),
                    "count": count,
                    "quantity": to_float(quantity) or 0,
                    "amount": to_float(amount) or 0,
                }
                for value, count, quantity, amount in rows
            ]

        totals = cls._apply_filters(
            db.session.query(
                func.count(PlantReplacement.id),
                func.coalesce(func.sum(PlantReplacement.quantity), 0),
                func.coalesce(func.sum(PlantReplacement.amount), 0),
            ),
            filters,
        ).one()

        return {
            "total_count": totals[0] or 0,
            "total_quantity": to_float(totals[1]) or 0,
            "total_amount": to_float(totals[2]) or 0,
            "by_category": _group(PlantReplacement.plant_category, "plant_category"),
            "by_reason": _group(PlantReplacement.reason, "replacement_reason"),
        }
