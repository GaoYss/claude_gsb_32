"""养护记录接口测试：重点覆盖与养护任务的状态联动。"""

from datetime import date


def test_create_record_without_task_is_allowed(api, make_space):
    space = make_space()
    data = api.data(api.post("/api/v1/maintenance-records", {
        "green_space_id": space.id,
        "record_date": "2026-04-02",
        "work_content": "日常巡查，清理零星垃圾与倒伏草本",
        "worker": "何丽萍",
        "work_hours": 2,
        "quality_result": "qualified",
    }), 201)
    assert data["record_no"] == f"MR-{date.today():%Y%m%d}-001"
    assert data["task"] is None
    assert data["green_space"]["id"] == space.id


def test_create_record_requires_green_space_or_task(api):
    response = api.post("/api/v1/maintenance-records", {
        "record_date": "2026-04-02",
        "work_content": "无归属记录",
    })
    assert response.status_code == 422
    assert response.get_json()["data"] == {"green_space_id": "请选择所属绿地或关联养护任务"}


def test_record_derives_green_space_from_task(api, make_task):
    task = make_task()
    data = api.data(api.post("/api/v1/maintenance-records", {
        "task_id": task.id,
        "record_date": "2026-03-12",
        "work_content": "修剪香樟下垂枝 32 株",
    }), 201)
    assert data["green_space_id"] == task.green_space_id
    assert data["task"]["task_no"] == task.task_no


def test_green_space_must_match_task(api, make_task, make_space):
    task = make_task()
    other = make_space(name="另一处绿地")
    response = api.post("/api/v1/maintenance-records", {
        "task_id": task.id,
        "green_space_id": other.id,
        "record_date": "2026-03-12",
        "work_content": "绿地与任务不匹配",
    })
    assert response.status_code == 422
    assert "不一致" in response.get_json()["data"]["green_space_id"]


def test_qualified_record_completes_task(api, make_task):
    task = make_task()
    assert api.data(api.get(f"/api/v1/maintenance-tasks/{task.id}"))["status"] == "pending"

    api.post("/api/v1/maintenance-records", {
        "task_id": task.id,
        "record_date": "2026-03-12",
        "work_content": "修剪完成，清运枝条 2 车",
        "quality_result": "qualified",
    })
    detail = api.data(api.get(f"/api/v1/maintenance-tasks/{task.id}"))
    assert detail["status"] == "completed"
    assert detail["completed_at"].startswith("2026-03-12")


def test_unqualified_record_blocks_task_completion(api, make_task):
    task = make_task()
    unqualified = api.data(api.post("/api/v1/maintenance-records", {
        "task_id": task.id,
        "record_date": "2026-03-12",
        "work_content": "修剪后现场未清理",
        "quality_result": "unqualified",
    }), 201)
    detail = api.data(api.get(f"/api/v1/maintenance-tasks/{task.id}"))
    assert detail["status"] == "in_progress"
    assert detail["completed_at"] is None

    # 存在不合格记录时，追加合格记录也不会自动完成，必须先整改
    api.post("/api/v1/maintenance-records", {
        "task_id": task.id,
        "record_date": "2026-03-15",
        "work_content": "整改复检合格",
        "quality_result": "qualified",
    })
    assert api.data(api.get(f"/api/v1/maintenance-tasks/{task.id}"))["status"] == "in_progress"

    # 把不合格记录改判为合格后，任务自动完成
    api.put(f"/api/v1/maintenance-records/{unqualified['id']}", {
        "task_id": task.id,
        "record_date": "2026-03-12",
        "work_content": "修剪后现场未清理，当日整改完成",
        "quality_result": "qualified",
    })
    assert api.data(api.get(f"/api/v1/maintenance-tasks/{task.id}"))["status"] == "completed"


def test_cancelled_task_rejects_new_record(api, make_task):
    task = make_task(status="cancelled")
    response = api.post("/api/v1/maintenance-records", {
        "task_id": task.id,
        "record_date": "2026-03-12",
        "work_content": "取消后补录",
    })
    assert response.status_code == 409
    assert "已取消" in response.get_json()["message"]


def test_record_date_cannot_precede_established_date(api, make_space):
    space = make_space(established_date=date(2020, 1, 1))
    response = api.post("/api/v1/maintenance-records", {
        "green_space_id": space.id,
        "record_date": "2019-12-31",
        "work_content": "建成前记录",
    })
    assert response.status_code == 422
    assert "建成日期" in response.get_json()["data"]["record_date"]


def test_delete_record_reverts_task_status(api, make_task):
    task = make_task()
    record = api.data(api.post("/api/v1/maintenance-records", {
        "task_id": task.id,
        "record_date": "2026-03-12",
        "work_content": "修剪完成",
        "quality_result": "qualified",
    }), 201)
    assert api.data(api.get(f"/api/v1/maintenance-tasks/{task.id}"))["status"] == "completed"

    api.delete(f"/api/v1/maintenance-records/{record['id']}")
    task_after = api.data(api.get(f"/api/v1/maintenance-tasks/{task.id}"))
    assert task_after["status"] == "pending"
    assert task_after["completed_at"] is None


def test_delete_record_cascades_replacements_and_reverts_all_aggregates(
    api, make_space, make_task, make_record, make_replacement
):
    """删除带更换明细的记录：明细级联删除，任务/完成率/最近养护日期一并回落。"""

    space = make_space()
    # 更早的一条独立记录，使被删记录不是该绿地唯一一次养护
    make_record(space=space, record_date=date(2026, 3, 1),
                work_content="月初日常巡查", quality_result="qualified")
    task = make_task(space=space, plan_date=date(2026, 3, 8))
    record = make_record(task=task, record_date=date(2026, 3, 12),
                         quality_result="qualified")
    make_replacement(record=record, replace_date=date(2026, 3, 12),
                     quantity=6, unit_price=100)

    # 删除前：任务已完成、完成率 100%、最近养护日期停在 3-12、有 1 条更换
    assert api.data(api.get(f"/api/v1/maintenance-tasks/{task.id}"))["status"] == "completed"
    profile = api.data(api.get(f"/api/v1/green-spaces/{space.id}/profile"))
    assert profile["statistics"]["last_maintenance_date"] == "2026-03-12"
    assert profile["statistics"]["replacement_count"] == 1
    assert api.data(api.get("/api/v1/statistics/overview"))["task"]["completion_rate"] == 100.0

    response = api.delete(f"/api/v1/maintenance-records/{record.id}")
    assert response.status_code == 200

    # 任务状态回落为待执行，完成时间清空
    task_after = api.data(api.get(f"/api/v1/maintenance-tasks/{task.id}"))
    assert task_after["status"] == "pending"
    assert task_after["completed_at"] is None
    # 任务进度中的更换口径同步清空
    assert task_after["progress"]["replacement_count"] == 0

    # 完成率回到 0
    overview = api.data(api.get("/api/v1/statistics/overview"))
    assert overview["task"]["by_status"]["completed"] == 0
    assert overview["task"]["completion_rate"] == 0.0

    # 绿地最近养护日期回退到上一条记录，更换明细与金额一并清掉
    profile = api.data(api.get(f"/api/v1/green-spaces/{space.id}/profile"))
    assert profile["statistics"]["last_maintenance_date"] == "2026-03-01"
    assert profile["statistics"]["record_count"] == 1
    assert profile["statistics"]["replacement_count"] == 0
    assert profile["statistics"]["replacement_amount"] == 0
    assert profile["recent_replacements"] == []

    # 关联的绿植更换明细已被级联删除，而不是留下孤立记录
    replacements = api.data(api.get("/api/v1/plant-replacements", green_space_id=space.id))
    assert replacements["meta"]["total"] == 0


def test_delete_record_rolls_back_when_sync_fails(
    api, make_task, make_record, make_replacement, monkeypatch
):
    """联动过程中抛错时整体回滚：记录、更换明细与任务状态都保持删除前。"""

    import pytest

    from app.extensions import db
    from app.models import MaintenanceRecord, PlantReplacement
    from app.services import MaintenanceRecordService

    task = make_task()
    record = make_record(task=task, quality_result="qualified")
    replacement = make_replacement(record=record)
    record_id, replacement_id = record.id, replacement.id

    def boom(*args, **kwargs):
        raise RuntimeError("模拟任务状态重算失败")

    monkeypatch.setattr(MaintenanceRecordService, "sync_task_status", boom)

    with pytest.raises(RuntimeError):
        MaintenanceRecordService.delete(record_id)

    # 回滚后记录与更换明细都还在，任务仍是已完成
    db.session.expire_all()
    assert db.session.get(MaintenanceRecord, record_id) is not None
    assert db.session.get(PlantReplacement, replacement_id) is not None
    detail = api.data(api.get(f"/api/v1/maintenance-tasks/{task.id}"))
    assert detail["status"] == "completed"
    assert api.get(f"/api/v1/maintenance-records/{record_id}").status_code == 200
    listed = api.data(
        api.get("/api/v1/plant-replacements", maintenance_record_id=record_id)
    )
    assert listed["meta"]["total"] == 1


def test_update_record_quality_resyncs_task(api, make_task):
    task = make_task()
    record = api.data(api.post("/api/v1/maintenance-records", {
        "task_id": task.id,
        "record_date": "2026-03-12",
        "work_content": "修剪完成",
        "quality_result": "qualified",
    }), 201)
    assert api.data(api.get(f"/api/v1/maintenance-tasks/{task.id}"))["status"] == "completed"

    api.put(f"/api/v1/maintenance-records/{record['id']}", {
        "task_id": task.id,
        "record_date": "2026-03-12",
        "work_content": "修剪完成，验收不合格",
        "quality_result": "unqualified",
    })
    assert api.data(api.get(f"/api/v1/maintenance-tasks/{task.id}"))["status"] == "in_progress"


def test_list_filters_and_summary(api, make_task, make_record):
    task = make_task()
    make_record(task=task, work_hours=6, quality_result="qualified")
    make_record(task=task, work_hours=4, quality_result="unqualified", record_date=date(2026, 3, 20))
    make_record(space=task.green_space, work_hours=2, quality_result="qualified",
                record_date=date(2026, 4, 1), work_content="日常巡查，清理园路落叶")

    data = api.data(api.get("/api/v1/maintenance-records", task_id=task.id))
    assert data["meta"]["total"] == 2
    assert data["summary"]["record_count"] == 2
    assert data["summary"]["total_work_hours"] == 10.0
    assert data["summary"]["quality_summary"] == {"qualified": 1, "pending": 0, "unqualified": 1}

    ranged = api.data(api.get("/api/v1/maintenance-records", date_from="2026-04-01",
                              date_to="2026-04-30"))
    assert ranged["meta"]["total"] == 1

    keyword = api.data(api.get("/api/v1/maintenance-records", keyword="下垂枝"))
    assert keyword["meta"]["total"] == 2
