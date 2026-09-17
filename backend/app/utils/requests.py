"""请求体解析。"""

from flask import request

from ..errors import BadRequestError


def json_body():
    """获取 JSON 请求体，非法或为空时给出明确提示。"""

    payload = request.get_json(silent=True)
    if payload is None:
        raise BadRequestError("请求体必须为 JSON 格式，并设置 Content-Type: application/json")
    return payload


def query_flag(name, default=False):
    value = request.args.get(name)
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y"}
