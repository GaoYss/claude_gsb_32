"""应用配置。

默认使用 SQLite 便于本地开发与测试，通过 DATABASE_URL 可切换为
PostgreSQL / MySQL（docker-compose 中即使用 PostgreSQL）。
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = Path(os.getenv("INSTANCE_DIR", BASE_DIR / "instance"))


def _bool_env(name, default):
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def default_database_uri():
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    return "sqlite:///" + (INSTANCE_DIR / "green_space.db").as_posix()


class Config:
    """基础配置。"""

    SECRET_KEY = os.getenv("SECRET_KEY", "green-space-dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or default_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 3600}

    API_PREFIX = "/api/v1"
    DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "10"))
    MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "100"))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # 启动时自动建表，便于本地与容器内快速验证；生产建议改用 Flask-Migrate。
    AUTO_CREATE_TABLES = _bool_env("AUTO_CREATE_TABLES", True)


class TestConfig(Config):
    """测试配置：内存库，建表交给测试夹具。"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
