from datetime import datetime, timedelta, timezone

from src.config import Config
from src.weather import MinutelyForecast, WeatherSnapshot


def make_config(**overrides) -> Config:
    defaults = {
        "owm_api_key": "test-key",
        "location_lat": 1.35,
        "location_lon": 103.82,
        "location_name": "TestCity",
        "poll_interval_minutes": 10,
        "rain_threshold_mm": 0.5,
        "alert_lead_minutes": 15,
    }
    return Config(**(defaults | overrides))


def make_snapshot(precip_values: list[float], start: datetime | None = None) -> WeatherSnapshot:
    start = start or datetime.now(timezone.utc)
    return WeatherSnapshot(
        minutely=[
            MinutelyForecast(dt=start + timedelta(minutes=i), precipitation=p)
            for i, p in enumerate(precip_values)
        ],
        current_rain_mm=0.0,
    )
