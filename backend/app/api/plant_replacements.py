"""绿植更换记录接口。"""

from flask import Blueprint, request

from ..schemas import validate_plant_replacement
from ..schemas.filters import replacement_filters
from ..services import PlantReplacementService
from ..utils.pagination import paginate, parse_page_args
from ..utils.requests import json_body
from ..utils.responses import created, ok

bp = Blueprint("plant_replacements", __name__)


@bp.get("/plant-replacements")
def list_replacements():
    filters = replacement_filters(request.args)
    page, page_size = parse_page_args()
    query = PlantReplacementService.list_replacements(filters, request.args)
    data = paginate(query, page, page_size)
    data["summary"] = PlantReplacementService.summary(filters)
    return ok(data)


@bp.get("/plant-replacements/summary")
def replacement_summary():
    return ok(PlantReplacementService.summary(replacement_filters(request.args)))


@bp.post("/plant-replacements")
def create_replacement():
    payload = validate_plant_replacement(json_body())
    replacement = PlantReplacementService.create(payload)
    return created(replacement.to_dict(detail=True), message="绿植更换记录登记成功")


@bp.get("/plant-replacements/<int:replacement_id>")
def get_replacement(replacement_id):
    return ok(PlantReplacementService.detail(replacement_id))


@bp.put("/plant-replacements/<int:replacement_id>")
def update_replacement(replacement_id):
    payload = validate_plant_replacement(json_body())
    replacement = PlantReplacementService.update(replacement_id, payload)
    return ok(replacement.to_dict(detail=True), message="绿植更换记录已更新")


@bp.delete("/plant-replacements/<int:replacement_id>")
def delete_replacement(replacement_id):
    PlantReplacementService.delete(replacement_id)
    return ok(None, message="绿植更换记录已删除")
