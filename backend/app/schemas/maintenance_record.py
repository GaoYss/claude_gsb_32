"""养护记录校验规则。"""

from ..constants import QUALITY_RESULT, WEATHER
from .common import PayloadValidator


def validate_maintenance_record(payload):
    return (
        PayloadValidator(payload)
        .integer("task_id", "关联任务", min_value=1)
        .integer("green_space_id", "所属绿地", min_value=1)
        .date("record_date", "养护日期", required=True)
        .text("work_content", "作业内容", required=True, max_length=4000)
        .string("worker", "作业人员", max_length=64)
        .number("work_hours", "工时", min_value=0, max_value=1000)
        .enum("weather", "天气", group=WEATHER)
        .text("materials", "使用材料/药剂", max_length=1000)
        .enum("quality_result", "质量评定", group=QUALITY_RESULT, default="pending")
        .text("issue_found", "发现问题", max_length=2000)
        .text("remark", "备注", max_length=2000)
        .done()
    )
