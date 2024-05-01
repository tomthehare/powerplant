from pydantic import BaseModel


class WaterQueueEntry(BaseModel):
    valve_id: int
    open_duration_seconds: int