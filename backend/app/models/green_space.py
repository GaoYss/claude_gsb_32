"""绿地台账模型。"""

from ..constants import GREEN_SPACE_STATUS, GREEN_SPACE_TYPE, MAINTENANCE_GRADE
from ..extensions import db
from ..utils.dates import format_date, format_datetime
from ..utils.numbers import to_float
from .mixins import TimestampMixin, quantity_column


class GreenSpace(TimestampMixin, db.Model):
    """城市绿地台账：一处绿地一条记录。"""

    __tablename__ = "green_space"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), nullable=False, unique=True, index=True)
    name = db.Column(db.String(128), nullable=False, index=True)
    district = db.Column(db.String(64), nullable=False, index=True)
    address = db.Column(db.String(255))
    green_type = db.Column(db.String(32), nullable=False, index=True)
    maintenance_grade = db.Column(db.String(16), nullable=False, default="level2", index=True)
    area_sqm = db.Column(quantity_column(), nullable=False, default=0)
    status = db.Column(db.String(16), nullable=False, default="normal", index=True)
    manager = db.Column(db.String(64))
    contact_phone = db.Column(db.String(32))
    plant_summary = db.Column(db.Text)
    established_date = db.Column(db.Date)
    remark = db.Column(db.Text)

    tasks = db.relationship(
        "MaintenanceTask", back_populates="green_space", cascade="all, delete-orphan"
    )
    records = db.relationship(
        "MaintenanceRecord", back_populates="green_space", cascade="all, delete-orphan"
    )
    replacements = db.relationship(
        "PlantReplacement", back_populates="green_space", cascade="all, delete-orphan"
    )

    def to_brief(self):
        """下拉框与关联展示用的精简结构。"""

        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "district": self.district,
        }

    def to_dict(self, detail=False):
        data = {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "district": self.district,
            "address": self.address,
            "green_type": self.green_type,
            "green_type_label": GREEN_SPACE_TYPE.label(self.green_type),
            "maintenance_grade": self.maintenance_grade,
            "maintenance_grade_label": MAINTENANCE_GRADE.label(self.maintenance_grade),
            "area_sqm": to_float(self.area_sqm),
            "status": self.status,
            "status_label": GREEN_SPACE_STATUS.label(self.status),
            "manager": self.manager,
            "contact_phone": self.contact_phone,
            "established_date": format_date(self.established_date),
            "created_at": format_datetime(self.created_at),
            "updated_at": format_datetime(self.updated_at),
        }
        if detail:
            data["plant_summary"] = self.plant_summary
            data["remark"] = self.remark
        return data
