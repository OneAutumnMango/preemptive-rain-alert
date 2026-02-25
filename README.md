# preemptive-rain-alert

Preemptive rain alert system — warns you *before* it starts raining.

Uses the [OpenWeatherMap One Call 3.0](https://openweathermap.org/api/one-call-3) API which provides **per-minute precipitation forecasts for the next hour** (free for first 1,000 calls/day).

## Quick Start

1. Get a free API key at https://home.openweathermap.org/users/sign_up
2. Subscribe to the One Call 3.0 API (free tier) at https://home.openweathermap.org/subscriptions
3. See the [example/](example/) directory for a docker-compose.yml and .env.example to get started

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OWM_API_KEY` | ✅ | | OpenWeatherMap API key |
| `LOCATION_LAT` | ✅ | | Latitude |
| `LOCATION_LON` | ✅ | | Longitude |
| `LOCATION_NAME` | ✅ | | Location name (for display) |
| `POLL_INTERVAL_MINUTES` | | 10 | How often to check |
| `RAIN_THRESHOLD_MM` | | 0.5 | Min precipitation to trigger alert (mm) |
| `ALERT_LEAD_MINUTES` | | 15 | How far ahead to look (max 60) |
| `APPRISE_URLS` | | | Comma-separated [Apprise URLs](https://github.com/caronc/apprise/wiki) (falls back to console) |

## Notifications

Notifications are powered by [Apprise](https://github.com/caronc/apprise), which supports 100+ services including Discord, Telegram, Slack, Email, WhatsApp (via Twilio), and more.

Set `APPRISE_URLS` with one or more comma-separated Apprise URLs. If left empty, alerts are printed to the console.

**Examples:**

| Service | URL format |
|---------|-----------|
| Discord | `discord://webhook_id/webhook_token` |
| Telegram | `tgram://bot_token/chat_id` |
| Slack | `slack://token_a/token_b/token_c/#channel` |
| Email (SMTP) | `mailto://user:pass@gmail.com` |
| Pushover | `pover://user_key@app_token` |
| ntfy | `ntfy://topic` |

Multiple services at once:

```env
APPRISE_URLS=discord://webhook_id/webhook_token,tgram://bot_token/chat_id
```

See the full list of supported services at https://github.com/caronc/apprise/wiki

## API Notes

The One Call 3.0 free tier gives you:
- **Minutely** precipitation forecast for the next **60 minutes**
- **Hourly** forecast for 48 hours
- **Current** conditions updated every minute

At the default 10-min poll interval that's 144 calls/day, well under the 1,000/day free limit.

