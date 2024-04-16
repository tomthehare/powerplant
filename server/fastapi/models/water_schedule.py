from pydantic import BaseModel


class WaterSchedule(BaseModel):
    hours: list[int]
    water_every_days: int