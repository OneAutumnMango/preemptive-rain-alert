# Contributing

## Setup

```sh
git clone git@github.com:DavidWhittam-eaton/preemptive-rain-alert.git
cd preemptive-rain-alert
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Running Locally

```sh
cp .env.example .env   # fill in your values
docker compose up --build
```

## Tests

```sh
python -m pytest tests/ -v
```

Tests mock the OpenWeatherMap API so no API key is needed.

## Docker Builds

- Push to `main` → publishes `ghcr.io/davidwhittam-eaton/preemptive-rain-alert:dev`
- Push tag `X.Y.Z` → publishes `:X.Y.Z` and `:X.Y`

## Project Structure

```
src/
  config.py    # pydantic-settings config (env vars)
  weather.py   # OpenWeatherMap API client
  alerter.py   # rain prediction logic
  notifier.py  # alert output (extend for webhooks/push/etc)
  main.py      # scheduler entrypoint
tests/
  test_rain_alert.py
```
