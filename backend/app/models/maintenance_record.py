"""养护记录模型。"""

from ..constants import QUALITY_RESULT, WEATHER
from ..extensions import db
from ..utils.dates import format_date, format_datetime
from ..utils.numbers import to_float
from .mixins import TimestampMixin, quantity_column


class MaintenanceRecord(TimestampMixin, db.Model):
    """养护记录录入：某次养护任务的作业明细，也可独立登记日常养护。"""

    __tablename__ = "maintenance_record"

    id = db.Column(db.Integer, primary_key=True)
    record_no = db.Column(db.String(32), nullable=False, unique=True, index=True)
    task_id = db.Column(
        db.Integer,
        db.ForeignKey("maintenance_task.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    green_space_id = db.Column(
        db.Integer, db.ForeignKey("green_space.id", ondelete="CASCADE"), nullable=False, index=True
    )
    record_date = db.Column(db.Date, nullable=False, index=True)
    work_content = db.Column(db.Text, nullable=False)
    worker = db.Column(db.String(64))
    work_hours = db.Column(quantity_column())
    weather = db.Column(db.String(16))
    materials = db.Column(db.Text)
    quality_result = db.Column(db.String(16), nullable=False, default="pending", index=True)
    issue_found = db.Column(db.Text)
    remark = db.Column(db.Text)

    task = db.relationship("MaintenanceTask", back_populates="records")
    green_space = db.relationship("GreenSpace", back_populates="records", lazy="joined")
    replacements = db.relationship("PlantReplacement", back_populates="record")

    def to_dict(self, detail=False):
        data = {
            "id": self.id,
            "record_no": self.record_no,
            "task_id": self.task_id,
            "task": (
                {
                    "id": self.task.id,
                    "task_no": self.task.task_no,
                    "title": self.task.title,
                    "status": self.task.status,
                }
                if self.task
                else None
            ),
            "green_space_id": self.green_space_id,
            "green_space": self.green_space.to_brief() if self.green_space else None,
            "record_date": format_date(self.record_date),
            "work_content": self.work_content,
            "worker": self.worker,
            "work_hours": to_float(self.work_hours),
            "weather": self.weather,
            "weather_label": WEATHER.label(self.weather) if self.weather else None,
            "quality_result": self.quality_result,
            "quality_result_label": QUALITY_RESULT.label(self.quality_result),
            "created_at": format_datetime(self.created_at),
            "updated_at": format_datetime(self.updated_at),
        }
        if detail:
            data["materials"] = self.materials
            data["issue_found"] = self.issue_found
            data["remark"] = self.remark
            data["replacements"] = [item.to_dict() for item in self.replacements]
        return data
