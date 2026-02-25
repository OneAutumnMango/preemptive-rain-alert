import asyncio
import time

import schedule

from .alerter import analyse
from .config import Config
from .notifier import notify
from .weather import fetch_weather


async def check() -> None:
    cfg = Config()
    try:
        snapshot = await fetch_weather(cfg)
    except RuntimeError as e:
        print(f"⚠ {e}", flush=True)
        return
    msg = analyse(cfg, snapshot)
    if msg:
        notify(msg)
    else:
        print(f"✓ No rain expected at {cfg.location_name}", flush=True)


def run_check() -> None:
    asyncio.run(check())


def main() -> None:
    cfg = Config()
    print(f"Starting rain alert for {cfg.location_name} "
          f"({cfg.location_lat}, {cfg.location_lon})")
    print(f"Polling every {cfg.poll_interval_minutes} min | "
          f"threshold {cfg.rain_threshold_mm} mm | "
          f"lead time {cfg.alert_lead_minutes} min")

    run_check()
    schedule.every(cfg.poll_interval_minutes).minutes.do(run_check)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
