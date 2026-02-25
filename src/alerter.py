from __future__ import annotations

from datetime import datetime, timezone

from .config import Config
from .weather import WeatherSnapshot


def analyse(cfg: Config, snapshot: WeatherSnapshot) -> str | None:
    """Return an alert message if rain is expected soon, else None."""
    now = datetime.now(timezone.utc)
    lead_seconds = cfg.alert_lead_minutes * 60

    upcoming = [
        m
        for m in snapshot.minutely
        if 0 <= (m.dt - now).total_seconds() <= lead_seconds
        and m.precipitation >= cfg.rain_threshold_mm
    ]

    if not upcoming:
        return None

    first = upcoming[0]
    minutes_away = int((first.dt - now).total_seconds() / 60)
    max_mm = max(m.precipitation for m in upcoming)

    return (
        f"🌧  Rain expected at {cfg.location_name} "
        f"in ~{minutes_away} min (up to {max_mm:.1f} mm/h)"
    )
