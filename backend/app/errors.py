"""统一业务异常与全局错误处理。"""

from .utils.responses import error_response


class ApiError(Exception):
    """业务异常基类：携带 HTTP 状态码与业务错误码。"""

    status_code = 400
    code = 40000

    def __init__(self, message, *, status_code=None, code=None, details=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code
        self.details = details

    def to_response(self):
        return error_response(
            self.message, code=self.code, status_code=self.status_code, details=self.details
        )


class BadRequestError(ApiError):
    status_code = 400
    code = 40000


class NotFoundError(ApiError):
    status_code = 404
    code = 40400

    def __init__(self, message="资源不存在", *, details=None):
        super().__init__(message, status_code=404, code=40400, details=details)


class ConflictError(ApiError):
    status_code = 409
    code = 40900


class ValidationError(ApiError):
    """字段级校验失败，details 为 {字段: 提示}。"""

    def __init__(self, message="提交的数据未通过校验", *, details=None):
        super().__init__(message, status_code=422, code=42200, details=details)


def register_error_handlers(app):
    """注册全局异常处理，保证接口始终返回统一结构。"""

    @app.errorhandler(ApiError)
    def handle_api_error(exc):
        return exc.to_response()

    @app.errorhandler(404)
    def handle_not_found(exc):
        return error_response("接口不存在", code=40400, status_code=404)

    @app.errorhandler(405)
    def handle_method_not_allowed(exc):
        return error_response("请求方法不被允许", code=40501, status_code=405)

    @app.errorhandler(Exception)
    def handle_unexpected(exc):
        app.logger.exception("未捕获的服务端异常: %s", exc)
        return error_response("服务器内部错误", code=50000, status_code=500)
