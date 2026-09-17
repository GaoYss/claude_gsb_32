"""应用工厂。

后端按「接口层 api → 校验层 schemas → 业务层 services → 模型层 models」分层：

- api：只负责解析 HTTP 入参、调用 service、组装统一响应；
- schemas：字段校验与查询条件解析；
- services：事务、编号生成与跨模块业务规则；
- models：SQLAlchemy 模型与序列化。
"""

from flask import Flask

from .api import register_blueprints
from .config import Config
from .errors import register_error_handlers
from .extensions import cors, db, migrate


def create_app(config_object=Config, **overrides):
    app = Flask(__name__)
    app.config.from_object(config_object)
    if overrides:
        app.config.update(overrides)

    # 中文不被转义，便于直接阅读接口返回
    app.json.ensure_ascii = False
    app.json.sort_keys = False

    _init_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)

    from .cli import register_cli

    register_cli(app)
    register_shell_context(app)
    _bootstrap_database(app)
    return app


def _init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    # 确保模型在 create_all / migrate 之前完成注册
    from . import models  # noqa: F401


def _bootstrap_database(app):
    """本地与容器环境自动建表；生产环境可关闭并改用迁移脚本。"""

    if not app.config.get("AUTO_CREATE_TABLES", True):
        return
    with app.app_context():
        db.create_all()


def register_shell_context(app):
    @app.shell_context_processor
    def shell_context():
        from . import models

        return {"db": db, **{name: getattr(models, name) for name in models.__all__}}
