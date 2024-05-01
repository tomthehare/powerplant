from typing import Optional

from pydantic import BaseModel

from models.plant_group import PlantGroup
from models.water_schedule import WaterSchedule


class Config(BaseModel):
    fan_temperature: int
    water_config: Optional[WaterSchedule]
    plant_groups: Optional[list]
