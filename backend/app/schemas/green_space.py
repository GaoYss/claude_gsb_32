"""绿地台账校验规则。"""

from ..constants import GREEN_SPACE_STATUS, GREEN_SPACE_TYPE, MAINTENANCE_GRADE
from .common import PHONE_PATTERN, PayloadValidator


def validate_green_space(payload):
    return (
        PayloadValidator(payload)
        .string("code", "绿地编号", max_length=32)
        .string("name", "绿地名称", required=True, max_length=128)
        .string("district", "所属行政区", required=True, max_length=64)
        .string("address", "详细地址", max_length=255)
        .enum("green_type", "绿地类型", group=GREEN_SPACE_TYPE, required=True)
        .enum("maintenance_grade", "养护等级", group=MAINTENANCE_GRADE, required=True)
        .enum("status", "养护状态", group=GREEN_SPACE_STATUS, default="normal")
        .number("area_sqm", "绿地面积", required=True, min_value=0, max_value=99999999)
        .string("manager", "养护负责人", max_length=64)
        .string("contact_phone", "联系电话", max_length=32, pattern=PHONE_PATTERN,
                pattern_message="联系电话格式不正确")
        .date("established_date", "建成日期")
        .text("plant_summary", "主要植物概况", max_length=2000)
        .text("remark", "备注", max_length=2000)
        .done()
    )
