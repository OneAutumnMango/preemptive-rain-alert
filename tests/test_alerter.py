from src.alerter import analyse

from .conftest import make_config, make_snapshot


class TestAnalyse:
    def test_returns_none_when_no_rain(self):
        cfg = make_config()
        snapshot = make_snapshot([0.0] * 60)
        assert analyse(cfg, snapshot) is None

    def test_returns_alert_when_rain_detected(self):
        cfg = make_config()
        precip = [0.0] * 5 + [1.2] + [0.0] * 54
        snapshot = make_snapshot(precip)
        msg = analyse(cfg, snapshot)
        assert msg is not None
        assert "TestCity" in msg
        assert "1.2" in msg

    def test_returns_none_when_below_threshold(self):
        cfg = make_config(rain_threshold_mm=2.0)
        snapshot = make_snapshot([0.0] * 5 + [1.0] + [0.0] * 54)
        assert analyse(cfg, snapshot) is None

    def test_returns_none_when_outside_lead_time(self):
        cfg = make_config(alert_lead_minutes=5)
        precip = [0.0] * 10 + [3.0] + [0.0] * 49
        snapshot = make_snapshot(precip)
        assert analyse(cfg, snapshot) is None

    def test_returns_max_precipitation_when_multiple_rain_minutes(self):
        cfg = make_config()
        precip = [0.0] * 3 + [0.5, 2.0, 0.8] + [0.0] * 54
        snapshot = make_snapshot(precip)
        msg = analyse(cfg, snapshot)
        assert msg is not None
        assert "2.0" in msg
