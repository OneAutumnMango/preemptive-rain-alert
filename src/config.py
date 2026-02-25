from pydantic_settings import BaseSettings


class Config(BaseSettings):
    owm_api_key: str
    location_lat: float
    location_lon: float
    location_name: str
    poll_interval_minutes: int = 10
    rain_threshold_mm: float = 0.5
    alert_lead_minutes: int = 15
    daily_api_limit: int = 950

    apprise_urls: str = ""
