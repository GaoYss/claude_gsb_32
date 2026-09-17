"""接口层：按业务模块拆分 Blueprint，统一挂载到 /api/v1。"""

from .green_spaces import bp as green_spaces_bp
from .maintenance_records import bp as maintenance_records_bp
from .maintenance_tasks import bp as maintenance_tasks_bp
from .meta import bp as meta_bp
from .plant_replacements import bp as plant_replacements_bp
from .statistics import bp as statistics_bp

BLUEPRINTS = (
    meta_bp,
    green_spaces_bp,
    maintenance_tasks_bp,
    maintenance_records_bp,
    plant_replacements_bp,
    statistics_bp,
)


def register_blueprints(app):
    prefix = app.config["API_PREFIX"]
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint, url_prefix=prefix)
