from pydantic import BaseModel


class Event(BaseModel):
    event_id: str
    subject_type: str
    subject_id: str
    timestamp: int
    verb: str
