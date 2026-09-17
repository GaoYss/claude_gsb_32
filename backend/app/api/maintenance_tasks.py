"""养护任务接口。"""

from flask import Blueprint, request

from ..schemas import validate_maintenance_task, validate_task_status
from ..schemas.filters import task_filters
from ..services import MaintenanceTaskService
from ..utils.pagination import paginate, parse_page_args
from ..utils.requests import json_body, query_flag
from ..utils.responses import created, ok

bp = Blueprint("maintenance_tasks", __name__)


@bp.get("/maintenance-tasks")
def list_tasks():
    filters = task_filters(request.args)
    page, page_size = parse_page_args()
    query = MaintenanceTaskService.list_tasks(filters, request.args)
    data = paginate(query, page, page_size, serializer=MaintenanceTaskService.serialize_row)
    data["summary"] = MaintenanceTaskService.status_summary()
    return ok(data)


@bp.post("/maintenance-tasks")
def create_task():
    payload = validate_maintenance_task(json_body())
    task = MaintenanceTaskService.create(payload)
    return created(task.to_dict(detail=True), message="养护任务登记成功")


@bp.get("/maintenance-tasks/<int:task_id>")
def get_task(task_id):
    return ok(MaintenanceTaskService.detail(task_id))


@bp.put("/maintenance-tasks/<int:task_id>")
def update_task(task_id):
    payload = validate_maintenance_task(json_body())
    task = MaintenanceTaskService.update(task_id, payload)
    return ok(task.to_dict(detail=True), message="养护任务已更新")


@bp.patch("/maintenance-tasks/<int:task_id>/status")
def change_task_status(task_id):
    """状态流转：待执行 / 进行中 / 已完成 / 已取消。"""

    payload = validate_task_status(json_body())
    task = MaintenanceTaskService.change_status(task_id, payload)
    return ok(task.to_dict(detail=True), message="任务状态已更新")


@bp.delete("/maintenance-tasks/<int:task_id>")
def delete_task(task_id):
    force = query_flag("force")
    result = MaintenanceTaskService.delete(task_id, force=force)
    return ok(result, message="养护任务已删除")
