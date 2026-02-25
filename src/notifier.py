from __future__ import annotations


def notify(message: str) -> None:
    """Send an alert. For now just prints — extend with webhooks/push/etc."""
    print(message, flush=True)
