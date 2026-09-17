"""养护记录接口。"""

from flask import Blueprint, request

from ..schemas import validate_maintenance_record
from ..schemas.filters import record_filters
from ..services import MaintenanceRecordService
from ..utils.pagination import paginate, parse_page_args
from ..utils.requests import json_body
from ..utils.responses import created, ok

bp = Blueprint("maintenance_records", __name__)


@bp.get("/maintenance-records")
def list_records():
    filters = record_filters(request.args)
    page, page_size = parse_page_args()
    query = MaintenanceRecordService.list_records(filters, request.args)
    data = paginate(query, page, page_size)
    data["summary"] = MaintenanceRecordService.summary(filters)
    return ok(data)


@bp.get("/maintenance-records/summary")
def records_summary():
    return ok(MaintenanceRecordService.summary(record_filters(request.args)))


@bp.post("/maintenance-records")
def create_record():
    payload = validate_maintenance_record(json_body())
    record = MaintenanceRecordService.create(payload)
    return created(record.to_dict(detail=True), message="养护记录录入成功")


@bp.get("/maintenance-records/<int:record_id>")
def get_record(record_id):
    return ok(MaintenanceRecordService.detail(record_id))


@bp.put("/maintenance-records/<int:record_id>")
def update_record(record_id):
    payload = validate_maintenance_record(json_body())
    record = MaintenanceRecordService.update(record_id, payload)
    return ok(record.to_dict(detail=True), message="养护记录已更新")


@bp.delete("/maintenance-records/<int:record_id>")
def delete_record(record_id):
    MaintenanceRecordService.delete(record_id)
    return ok(None, message="养护记录已删除")
