"""养护任务校验规则。"""

from ..constants import TASK_PRIORITY, TASK_STATUS, TASK_TYPE
from .common import PayloadValidator


def validate_maintenance_task(payload):
    return (
        PayloadValidator(payload)
        .string("task_no", "任务编号", max_length=32)
        .integer("green_space_id", "所属绿地", required=True, min_value=1)
        .string("title", "任务名称", required=True, max_length=128)
        .enum("task_type", "养护类型", group=TASK_TYPE, required=True)
        .date("plan_date", "计划养护日期", required=True)
        .enum("priority", "优先级", group=TASK_PRIORITY, default="medium")
        .string("executor", "执行班组/负责人", max_length=64)
        .enum("status", "任务状态", group=TASK_STATUS, default="pending")
        .text("description", "任务说明", max_length=2000)
        .done()
    )


def validate_task_status(payload):
    """任务状态流转：只允许变更状态与说明。"""

    return (
        PayloadValidator(payload)
        .enum("status", "任务状态", group=TASK_STATUS, required=True)
        .text("description", "任务说明", max_length=2000)
        .done()
    )
