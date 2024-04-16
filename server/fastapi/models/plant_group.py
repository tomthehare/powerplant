from pydantic import BaseModel


class PlantGroup(BaseModel):
    valve_id: int
    description: str
    open_duration_seconds: int