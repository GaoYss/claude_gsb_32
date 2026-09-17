"""跨模块端到端流程测试。"""


def test_green_space_lifecycle_from_ledger_to_replacement(api):
    """绿地建档 → 任务登记 → 记录录入 → 绿植更换 → 档案与看板联动。"""

    space = api.data(api.post("/api/v1/green-spaces", {
        "name": "滨江公园樱花大道",
        "district": "滨江区",
        "green_type": "park",
        "maintenance_grade": "level1",
        "area_sqm": 23800,
        "manager": "林轶",
        "contact_phone": "0571-86608812",
        "established_date": "2018-03-20",
    }), 201)
    space_id = space["id"]

    task = api.data(api.post("/api/v1/maintenance-tasks", {
        "green_space_id": space_id,
        "title": "樱花树越冬修剪",
        "task_type": "prune",
        "plan_date": "2026-03-05",
        "priority": "high",
        "executor": "绿化一班",
    }), 201)
    assert task["status"] == "pending"

    record = api.data(api.post("/api/v1/maintenance-records", {
        "task_id": task["id"],
        "record_date": "2026-03-06",
        "work_content": "修剪染井吉野樱 46 株，清运枝条 3 车",
        "worker": "王海涛",
        "work_hours": 8,
        "weather": "sunny",
        "quality_result": "qualified",
    }), 201)
    assert record["green_space_id"] == space_id

    replacement = api.data(api.post("/api/v1/plant-replacements", {
        "green_space_id": space_id,
        "maintenance_record_id": record["id"],
        "plant_name": "染井吉野樱",
        "plant_category": "tree",
        "spec": "胸径 12-14cm",
        "quantity": 6,
        "unit": "plant",
        "reason": "dead",
        "old_plant_status": "dead",
        "replace_date": "2026-03-08",
        "supplier": "临安绿源苗圃",
        "unit_price": 680,
        "operator": "王海涛",
    }), 201)
    assert replacement["amount"] == 4080.0

    # 任务因合格记录自动完成
    task_detail = api.data(api.get(f"/api/v1/maintenance-tasks/{task['id']}"))
    assert task_detail["status"] == "completed"
    assert task_detail["progress"]["replacement_amount"] == 4080.0

    # 绿地档案汇总了一处绿地的全部养护数据
    profile = api.data(api.get(f"/api/v1/green-spaces/{space_id}/profile"))
    statistics = profile["statistics"]
    assert statistics["record_count"] == 1
    assert statistics["total_work_hours"] == 8.0
    assert statistics["replacement_quantity"] == 6.0
    assert statistics["replacement_amount"] == 4080.0
    assert statistics["task_status"]["completed"] == 1
    assert statistics["last_maintenance_date"] == "2026-03-06"
    assert profile["replacement_summary"][0]["reason"] == "dead"
    assert profile["recent_tasks"][0]["task_no"] == task["task_no"]
    assert profile["recent_records"][0]["record_no"] == record["record_no"]

    # 看板总览同步反映新增数据
    overview = api.data(api.get("/api/v1/statistics/overview"))
    assert overview["green_space"]["total"] == 1
    assert overview["task"]["by_status"]["completed"] == 1
    assert overview["replacement"]["total_amount"] == 4080.0

    # 台账列表带出统计列
    listing = api.data(api.get("/api/v1/green-spaces"))
    assert listing["items"][0]["statistics"]["record_count"] == 1
    assert listing["items"][0]["statistics"]["last_maintenance_date"] == "2026-03-06"


def test_task_and_record_codes_increase_in_sequence(api, make_space):
    space = make_space()
    task_payload = {
        "green_space_id": space.id,
        "title": "除草作业",
        "task_type": "weed",
        "plan_date": "2026-05-01",
    }
    first = api.data(api.post("/api/v1/maintenance-tasks", task_payload), 201)
    second = api.data(api.post("/api/v1/maintenance-tasks", task_payload), 201)
    assert first["task_no"].endswith("-001")
    assert second["task_no"].endswith("-002")

    record_payload = {
        "green_space_id": space.id,
        "record_date": "2026-05-02",
        "work_content": "清除绿篱内杂草约 800 平方米",
        "quality_result": "qualified",
    }
    first_record = api.data(api.post("/api/v1/maintenance-records", record_payload), 201)
    second_record = api.data(api.post("/api/v1/maintenance-records", record_payload), 201)
    assert first_record["record_no"].endswith("-001")
    assert second_record["record_no"].endswith("-002")


def test_demo_seed_produces_consistent_aggregates(api, seeded):
    """校验演示数据在多个聚合口径下保持一致。"""

    dashboard = api.data(api.get("/api/v1/statistics/dashboard"))
    overview = dashboard["overview"]
    assert overview["record"]["total"] == seeded["maintenance_record"]
    assert overview["replacement"]["total"] == seeded["plant_replacement"]
    assert overview["task"]["total"] == seeded["maintenance_task"]

    records = api.data(api.get("/api/v1/maintenance-records", page_size=100))
    assert records["meta"]["total"] == seeded["maintenance_record"]
    assert len(records["items"]) == seeded["maintenance_record"]

    spaces = api.data(api.get("/api/v1/green-spaces", page_size=100))
    total_records_from_spaces = sum(
        item["statistics"]["record_count"] for item in spaces["items"]
    )
    assert total_records_from_spaces == seeded["maintenance_record"]
