"""绿植更换记录校验规则。"""

from ..constants import MEASURE_UNIT, OLD_PLANT_STATUS, PLANT_CATEGORY, REPLACEMENT_REASON
from .common import PayloadValidator


def validate_plant_replacement(payload):
    return (
        PayloadValidator(payload)
        .integer("green_space_id", "所属绿地", required=True, min_value=1)
        .integer("maintenance_record_id", "关联养护记录", min_value=1)
        .string("plant_name", "植株名称", required=True, max_length=96)
        .enum("plant_category", "植物类别", group=PLANT_CATEGORY, required=True)
        .string("spec", "规格", max_length=64)
        .number("quantity", "更换数量", required=True, min_value=0.01, max_value=999999)
        .enum("unit", "计量单位", group=MEASURE_UNIT, default="plant")
        .enum("reason", "更换原因", group=REPLACEMENT_REASON, required=True)
        .enum("old_plant_status", "原植株状况", group=OLD_PLANT_STATUS)
        .date("replace_date", "更换日期", required=True)
        .string("supplier", "供苗单位", max_length=96)
        .number("unit_price", "单价", min_value=0, max_value=99999999)
        .string("operator", "登记人", max_length=64)
        .text("remark", "备注", max_length=2000)
        .done()
    )
