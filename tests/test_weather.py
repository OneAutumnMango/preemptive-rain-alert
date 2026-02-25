from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.weather import RateLimiter, fetch_weather

from .conftest import make_config


class TestFetchWeather:
    @pytest.mark.asyncio
    async def test_returns_snapshot_when_valid_response(self):
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
    async def test_returns_empty_when_missing_minutely(self):
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


class TestRateLimiter:
    def test_check_returns_true_when_under_limit(self):
        rl = RateLimiter()
        assert rl.check(5) is True
        rl.increment()
        assert rl.count == 1
        assert rl.check(5) is True

    def test_check_returns_false_when_at_limit(self):
        rl = RateLimiter()
        for _ in range(5):
            rl.increment()
        assert rl.check(5) is False

    def test_check_resets_count_when_new_day(self):
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
    async def test_raises_error_when_limit_reached(self):
        rl = RateLimiter()
        for _ in range(10):
            rl.increment()

        with patch("src.weather.rate_limiter", rl):
            cfg = make_config(daily_api_limit=10)
            with pytest.raises(RuntimeError, match="Daily API limit reached"):
                await fetch_weather(cfg)
