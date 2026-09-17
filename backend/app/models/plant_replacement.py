"""绿植更换记录模型。"""

from ..constants import MEASURE_UNIT, OLD_PLANT_STATUS, PLANT_CATEGORY, REPLACEMENT_REASON
from ..extensions import db
from ..utils.dates import format_date, format_datetime
from ..utils.numbers import to_float
from .mixins import TimestampMixin, amount_column, quantity_column


class PlantReplacement(TimestampMixin, db.Model):
    """绿植更换记录：绿地内植株的更换、补植与品种改造。"""

    __tablename__ = "plant_replacement"

    id = db.Column(db.Integer, primary_key=True)
    replacement_no = db.Column(db.String(32), nullable=False, unique=True, index=True)
    green_space_id = db.Column(
        db.Integer, db.ForeignKey("green_space.id", ondelete="CASCADE"), nullable=False, index=True
    )
    maintenance_record_id = db.Column(
        db.Integer,
        db.ForeignKey("maintenance_record.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    plant_name = db.Column(db.String(96), nullable=False, index=True)
    plant_category = db.Column(db.String(32), nullable=False, index=True)
    spec = db.Column(db.String(64))
    quantity = db.Column(quantity_column(), nullable=False, default=0)
    unit = db.Column(db.String(16), nullable=False, default="plant")
    reason = db.Column(db.String(32), nullable=False, index=True)
    old_plant_status = db.Column(db.String(16))
    replace_date = db.Column(db.Date, nullable=False, index=True)
    supplier = db.Column(db.String(96))
    unit_price = db.Column(amount_column())
    amount = db.Column(amount_column())
    operator = db.Column(db.String(64))
    remark = db.Column(db.Text)

    green_space = db.relationship("GreenSpace", back_populates="replacements", lazy="joined")
    record = db.relationship("MaintenanceRecord", back_populates="replacements")

    def to_dict(self, detail=False):
        data = {
            "id": self.id,
            "replacement_no": self.replacement_no,
            "green_space_id": self.green_space_id,
            "green_space": self.green_space.to_brief() if self.green_space else None,
            "maintenance_record_id": self.maintenance_record_id,
            "record": (
                {
                    "id": self.record.id,
                    "record_no": self.record.record_no,
                    "record_date": format_date(self.record.record_date),
                }
                if self.record
                else None
            ),
            "plant_name": self.plant_name,
            "plant_category": self.plant_category,
            "plant_category_label": PLANT_CATEGORY.label(self.plant_category),
            "spec": self.spec,
            "quantity": to_float(self.quantity),
            "unit": self.unit,
            "unit_label": MEASURE_UNIT.label(self.unit),
            "reason": self.reason,
            "reason_label": REPLACEMENT_REASON.label(self.reason),
            "old_plant_status": self.old_plant_status,
            "old_plant_status_label": (
                OLD_PLANT_STATUS.label(self.old_plant_status) if self.old_plant_status else None
            ),
            "replace_date": format_date(self.replace_date),
            "supplier": self.supplier,
            "unit_price": to_float(self.unit_price),
            "amount": to_float(self.amount),
            "operator": self.operator,
            "created_at": format_datetime(self.created_at),
            "updated_at": format_datetime(self.updated_at),
        }
        if detail:
            data["remark"] = self.remark
        return data
