"""绿地台账接口。"""

from flask import Blueprint, request

from ..schemas import green_space_filters, validate_green_space
from ..services import GreenSpaceService
from ..utils.pagination import paginate, parse_page_args
from ..utils.requests import json_body, query_flag
from ..utils.responses import created, ok

bp = Blueprint("green_spaces", __name__)


@bp.get("/green-spaces")
def list_green_spaces():
    """台账列表：支持关键字、类型、等级、状态、行政区过滤 + 排序 + 分页。"""

    filters = green_space_filters(request.args)
    page, page_size = parse_page_args()
    query = GreenSpaceService.list_spaces(filters, request.args)
    data = paginate(query, page, page_size, serializer=GreenSpaceService.serialize_row)
    data["summary"] = GreenSpaceService.filtered_summary(filters)
    return ok(data)


@bp.get("/green-spaces/options")
def green_space_options():
    """下拉选项（仅未归档绿地）。"""

    keyword = (request.args.get("keyword") or "").strip() or None
    return ok({"items": GreenSpaceService.options(keyword=keyword)})


@bp.get("/green-spaces/districts")
def districts():
    return ok({"items": GreenSpaceService.districts()})


@bp.post("/green-spaces")
def create_green_space():
    payload = validate_green_space(json_body())
    space = GreenSpaceService.create(payload)
    return created(space.to_dict(detail=True), message="绿地台账创建成功")


@bp.get("/green-spaces/<int:space_id>")
def get_green_space(space_id):
    return ok(GreenSpaceService.get(space_id).to_dict(detail=True))


@bp.get("/green-spaces/<int:space_id>/profile")
def green_space_profile(space_id):
    """绿地档案：台账信息 + 养护概览 + 近期任务/记录/更换。"""

    return ok(GreenSpaceService.detail(space_id))


@bp.put("/green-spaces/<int:space_id>")
def update_green_space(space_id):
    payload = validate_green_space(json_body())
    space = GreenSpaceService.update(space_id, payload)
    return ok(space.to_dict(detail=True), message="绿地台账已更新")


@bp.delete("/green-spaces/<int:space_id>")
def delete_green_space(space_id):
    """删除台账。存在关联业务数据时需显式 force=true 才会级联清理。"""

    force = query_flag("force")
    result = GreenSpaceService.delete(space_id, force=force)
    return ok(result, message="绿地台账及其关联数据已删除" if force else "绿地台账已删除")
