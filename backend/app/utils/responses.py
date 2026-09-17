"""统一响应结构。

成功：{"success": true, "code": 0, "message": "ok", "data": ...}
失败：{"success": false, "code": 4xxxx, "message": "...", "data": details}
"""

from flask import jsonify


def ok(data=None, message="ok", status_code=200):
    return jsonify({"success": True, "code": 0, "message": message, "data": data}), status_code


def created(data=None, message="创建成功"):
    return ok(data=data, message=message, status_code=201)


def error_response(message, code=40000, status_code=400, details=None):
    payload = {
        "success": False,
        "code": code,
        "message": message,
        "data": details if details is not None else None,
    }
    return jsonify(payload), status_code
