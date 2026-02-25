from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

import httpx

from .config import Config

OWM_ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"


@dataclass
class RateLimiter:
    _date: date = field(default_factory=date.today)
    _count: int = 0

    def check(self, limit: int) -> bool:
        today = date.today()
        if today != self._date:
            self._date = today
            self._count = 0
        return self._count < limit

    def increment(self) -> None:
        self._count += 1

    @property
    def count(self) -> int:
        return self._count


rate_limiter = RateLimiter()


@dataclass
class MinutelyForecast:
    dt: datetime
    precipitation: float  # mm


@dataclass
class WeatherSnapshot:
    minutely: list[MinutelyForecast]
    current_rain_mm: float


async def fetch_weather(cfg: Config) -> WeatherSnapshot:
    if not rate_limiter.check(cfg.daily_api_limit):
        raise RuntimeError(
            f"Daily API limit reached ({cfg.daily_api_limit} calls). "
            f"Skipping until tomorrow."
        )

    params = {
        "lat": cfg.location_lat,
        "lon": cfg.location_lon,
        "appid": cfg.owm_api_key,
        "exclude": "daily,hourly,alerts",
        "units": "metric",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(OWM_ONECALL_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    minutely = [
        MinutelyForecast(
            dt=datetime.fromtimestamp(m["dt"], tz=timezone.utc),
            precipitation=m.get("precipitation", 0.0),
        )
        for m in data.get("minutely", [])
    ]

    rate_limiter.increment()

    current = data.get("current", {})
    current_rain = current.get("rain", {}).get("1h", 0.0)

    return WeatherSnapshot(minutely=minutely, current_rain_mm=current_rain)
