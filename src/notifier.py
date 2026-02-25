from __future__ import annotations

import apprise

from .config import Config


def notify(cfg: Config, message: str) -> None:
    if not cfg.apprise_urls:
        print(message, flush=True)
        return
    ap = apprise.Apprise()
    for url in cfg.apprise_urls.split(","):
        ap.add(url.strip())
    ap.notify(body=message, title="Rain Alert")
