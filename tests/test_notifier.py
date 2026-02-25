from unittest.mock import MagicMock, patch

from src.notifier import notify

from .conftest import make_config


class TestNotify:
    def test_prints_to_console_when_no_urls(self, capsys):
        cfg = make_config()
        notify(cfg, "rain incoming")
        assert "rain incoming" in capsys.readouterr().out

    def test_prints_to_console_when_empty_string(self, capsys):
        cfg = make_config(apprise_urls="")
        notify(cfg, "hello")
        assert "hello" in capsys.readouterr().out

    def test_calls_apprise_when_single_url(self):
        cfg = make_config(apprise_urls="json://localhost/path")
        with patch("src.notifier.apprise.Apprise") as MockApprise:
            mock_ap = MagicMock()
            MockApprise.return_value = mock_ap
            notify(cfg, "rain incoming")
            mock_ap.add.assert_called_once_with("json://localhost/path")
            mock_ap.notify.assert_called_once_with(
                body="rain incoming", title="Rain Alert"
            )

    def test_adds_all_services_when_multiple_urls(self):
        cfg = make_config(apprise_urls="json://a, json://b")
        with patch("src.notifier.apprise.Apprise") as MockApprise:
            mock_ap = MagicMock()
            MockApprise.return_value = mock_ap
            notify(cfg, "msg")
            assert mock_ap.add.call_count == 2
            mock_ap.add.assert_any_call("json://a")
            mock_ap.add.assert_any_call("json://b")

    def test_strips_whitespace_when_urls_have_spaces(self):
        cfg = make_config(apprise_urls="  json://a  ,  json://b  ")
        with patch("src.notifier.apprise.Apprise") as MockApprise:
            mock_ap = MagicMock()
            MockApprise.return_value = mock_ap
            notify(cfg, "msg")
            mock_ap.add.assert_any_call("json://a")
            mock_ap.add.assert_any_call("json://b")

    def test_skips_console_when_urls_set(self, capsys):
        cfg = make_config(apprise_urls="json://localhost/path")
        with patch("src.notifier.apprise.Apprise") as MockApprise:
            mock_ap = MagicMock()
            MockApprise.return_value = mock_ap
            notify(cfg, "rain incoming")
        assert capsys.readouterr().out == ""
