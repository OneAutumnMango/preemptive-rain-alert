from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.alerter import analyse
from src.config import Config
from src.weather import MinutelyForecast, RateLimiter, WeatherSnapshot, fetch_weather


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


# -- alerter tests --

class TestAnalyse:
    def test_no_rain(self):
        cfg = make_config()
        snapshot = make_snapshot([0.0] * 60)
        assert analyse(cfg, snapshot) is None

    def test_rain_detected(self):
        cfg = make_config()
        precip = [0.0] * 5 + [1.2] + [0.0] * 54
        snapshot = make_snapshot(precip)
        msg = analyse(cfg, snapshot)
        assert msg is not None
        assert "TestCity" in msg
        assert "1.2" in msg

    def test_rain_below_threshold_ignored(self):
        cfg = make_config(rain_threshold_mm=2.0)
        snapshot = make_snapshot([0.0] * 5 + [1.0] + [0.0] * 54)
        assert analyse(cfg, snapshot) is None

    def test_rain_outside_lead_time_ignored(self):
        cfg = make_config(alert_lead_minutes=5)
        precip = [0.0] * 10 + [3.0] + [0.0] * 49
        snapshot = make_snapshot(precip)
        assert analyse(cfg, snapshot) is None

    def test_multiple_rain_minutes(self):
        cfg = make_config()
        precip = [0.0] * 3 + [0.5, 2.0, 0.8] + [0.0] * 54
        snapshot = make_snapshot(precip)
        msg = analyse(cfg, snapshot)
        assert msg is not None
        assert "2.0" in msg


# -- weather fetch tests --

class TestFetchWeather:
    @pytest.mark.asyncio
    async def test_parses_response(self):
        now = int(datetime.now(timezone.utc).timestamp())
        mock_data = {
            "current": {"rain": {"1h": 0.3}},
            "minutely": [
                {"dt": now + i * 60, "precipitation": 0.1 * i}
                for i in range(60)
            ],
        }

        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = lambda: None

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.weather.httpx.AsyncClient", return_value=mock_client):
            cfg = make_config()
            snapshot = await fetch_weather(cfg)

        assert len(snapshot.minutely) == 60
        assert snapshot.current_rain_mm == 0.3
        assert snapshot.minutely[0].precipitation == 0.0
        assert snapshot.minutely[5].precipitation == pytest.approx(0.5)

    @pytest.mark.asyncio
    async def test_handles_missing_minutely(self):
        mock_data = {"current": {}}

        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = lambda: None

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.weather.httpx.AsyncClient", return_value=mock_client):
            cfg = make_config()
            snapshot = await fetch_weather(cfg)

        assert snapshot.minutely == []
        assert snapshot.current_rain_mm == 0.0


# -- rate limiter tests --

class TestRateLimiter:
    def test_allows_under_limit(self):
        rl = RateLimiter()
        assert rl.check(5) is True
        rl.increment()
        assert rl.count == 1
        assert rl.check(5) is True

    def test_blocks_at_limit(self):
        rl = RateLimiter()
        for _ in range(5):
            rl.increment()
        assert rl.check(5) is False

    def test_resets_on_new_day(self):
        rl = RateLimiter()
        for _ in range(5):
            rl.increment()
        assert rl.check(5) is False

        with patch("src.weather.date") as mock_date:
            mock_date.today.return_value = date.today() + timedelta(days=1)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            assert rl.check(5) is True
            assert rl.count == 0

    @pytest.mark.asyncio
    async def test_fetch_blocked_at_limit(self):
        rl = RateLimiter()
        for _ in range(10):
            rl.increment()

        with patch("src.weather.rate_limiter", rl):
            cfg = make_config(daily_api_limit=10)
            with pytest.raises(RuntimeError, match="Daily API limit reached"):
                await fetch_weather(cfg)
