"""分页查询与结果封装。"""

from flask import current_app, request


def parse_page_args(args=None):
    """从查询参数解析页码与每页条数，并做上下限保护。"""

    args = args if args is not None else request.args
    default_size = current_app.config["DEFAULT_PAGE_SIZE"]
    max_size = current_app.config["MAX_PAGE_SIZE"]

    try:
        page = int(args.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = int(args.get("page_size", default_size))
    except (TypeError, ValueError):
        page_size = default_size

    return max(page, 1), min(max(page_size, 1), max_size)


def paginate(query, page, page_size, serializer=None):
    """执行分页查询并返回统一结构。"""

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    serializer = serializer or (lambda item: item.to_dict())
    return {
        "items": [serializer(item) for item in pagination.items],
        "meta": {
            "page": pagination.page,
            "page_size": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        },
    }
