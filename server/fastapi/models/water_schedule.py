from pydantic import BaseModel


class WaterSchedule(BaseModel):
    hours: list
    water_every_days: int
