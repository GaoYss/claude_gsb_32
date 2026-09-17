"""绿地台账接口测试。"""

from datetime import date


def space_payload(**overrides):
    payload = {
        "name": "运河文化公园",
        "district": "拱墅区",
        "address": "运河东路 128 号",
        "green_type": "park",
        "maintenance_grade": "level1",
        "area_sqm": 46200,
        "manager": "俞晓慧",
        "contact_phone": "0571-88221009",
        "plant_summary": "垂柳 120 株、麦冬地被 12000 平方米",
        "established_date": "2012-09-28",
    }
    payload.update(overrides)
    return payload


def test_create_generates_code_with_year_prefix(api):
    data = api.data(api.post("/api/v1/green-spaces", space_payload()), 201)
    assert data["code"] == f"GS-{date.today():%Y}-0001"
    assert data["green_type_label"] == "公园绿地"
    assert data["status"] == "normal"
    assert data["area_sqm"] == 46200.0


def test_create_keeps_custom_code_and_rejects_duplicate(api):
    first = api.data(api.post("/api/v1/green-spaces", space_payload(code="GS-XH-0007")), 201)
    assert first["code"] == "GS-XH-0007"

    response = api.post("/api/v1/green-spaces", space_payload(name="重复编号绿地", code="GS-XH-0007"))
    assert response.status_code == 409
    assert "已存在" in response.get_json()["message"]


def test_create_reports_field_errors_together(api):
    response = api.post("/api/v1/green-spaces", {
        "name": "",
        "district": "拱墅区",
        "green_type": "unknown-type",
        "maintenance_grade": "level9",
        "area_sqm": -5,
        "contact_phone": "abc",
        "established_date": "2012/13/40",
    })
    assert response.status_code == 422
    details = response.get_json()["data"]
    assert set(details) == {
        "name", "green_type", "maintenance_grade", "area_sqm", "contact_phone", "established_date"
    }
    assert "取值不合法" in details["green_type"]


def test_list_supports_keyword_and_enum_filters(api):
    api.post("/api/v1/green-spaces", space_payload())
    api.post("/api/v1/green-spaces", space_payload(name="西溪里小区绿地", district="西湖区",
                                                  address="文二西路 788 号",
                                                  green_type="residential", maintenance_grade="level3"))

    data = api.data(api.get("/api/v1/green-spaces", keyword="运河"))
    assert data["meta"]["total"] == 1
    assert data["items"][0]["name"] == "运河文化公园"
    assert data["summary"]["total_area"] == 46200.0

    data = api.data(api.get("/api/v1/green-spaces", green_type="residential", district="西湖区"))
    assert [item["name"] for item in data["items"]] == ["西溪里小区绿地"]

    # 非法枚举值被忽略，等价于不过滤
    data = api.data(api.get("/api/v1/green-spaces", green_type="not-a-type"))
    assert data["meta"]["total"] == 2


def test_list_supports_sorting_and_pagination(api):
    api.post("/api/v1/green-spaces", space_payload(name="小绿地", area_sqm=100))
    api.post("/api/v1/green-spaces", space_payload(name="大绿地", area_sqm=9000))

    data = api.data(api.get("/api/v1/green-spaces", sort="area_sqm", order="desc", page_size=1))
    assert data["items"][0]["name"] == "大绿地"
    assert data["meta"] == {"page": 1, "page_size": 1, "total": 2, "pages": 2}

    page2 = api.data(api.get("/api/v1/green-spaces", sort="area_sqm", order="desc",
                             page_size=1, page=2))
    assert page2["items"][0]["name"] == "小绿地"


def test_options_excludes_archived(api, make_space):
    make_space(name="在用绿地")
    make_space(name="归档绿地", status="archived")
    data = api.data(api.get("/api/v1/green-spaces/options"))
    assert [item["name"] for item in data["items"]] == ["在用绿地"]


def test_update_ignores_code_change(api, make_space):
    space = make_space(code="GS-FIX-0001")
    data = api.data(api.put(f"/api/v1/green-spaces/{space.id}", space_payload(code="GS-NEW-9999")))
    assert data["code"] == "GS-FIX-0001"
    assert data["name"] == "运河文化公园"


def test_detail_and_profile_aggregate_related_data(api, make_task, make_record):
    task = make_task()
    make_record(task=task, work_hours=8)
    make_record(task=task, work_hours=4, quality_result="pending", record_date=date(2026, 3, 20))

    data = api.data(api.get(f"/api/v1/green-spaces/{task.green_space_id}/profile"))
    assert data["green_space"]["name"] == task.green_space.name
    assert data["statistics"]["record_count"] == 2
    assert data["statistics"]["total_work_hours"] == 12.0
    assert data["statistics"]["last_maintenance_date"] == "2026-03-20"
    assert data["statistics"]["task_status"]["completed"] == 1
    assert len(data["recent_records"]) == 2


def test_delete_is_blocked_until_force(api, make_task):
    task = make_task()
    space_id = task.green_space_id

    response = api.delete(f"/api/v1/green-spaces/{space_id}")
    assert response.status_code == 409
    assert response.get_json()["data"]["maintenance_task"] == 1

    data = api.data(api.delete(f"/api/v1/green-spaces/{space_id}", force="true"))
    assert data == {"maintenance_task": 1, "maintenance_record": 0, "plant_replacement": 0}
    assert api.get(f"/api/v1/green-spaces/{space_id}").status_code == 404
