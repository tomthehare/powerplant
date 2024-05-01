from pydantic import BaseModel

class WeatherSample(BaseModel):
    timestamp: int
    humidity: float
    temperature: float
    location: str