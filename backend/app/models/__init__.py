"""模型包：导入全部模型，保证 db.create_all() 能建全表。"""

from .green_space import GreenSpace
from .maintenance_record import MaintenanceRecord
from .maintenance_task import MaintenanceTask
from .plant_replacement import PlantReplacement

__all__ = ["GreenSpace", "MaintenanceTask", "MaintenanceRecord", "PlantReplacement"]
