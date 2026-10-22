"""Start InstallScout (bruges også af den portable .exe)."""

from __future__ import annotations

import json
import os
import ssl
import sys
import threading
import time
import urllib.request
from datetime import datetime, timezone

APP_KEY = "A-EU-9748558859"
EVENT_URL = "https://eu.aptabase.com/api/v0/event"
SESSION_SECONDS = 60 * 60
SDK_VERSION = "installscout-win@1"


def session_path() -> str:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "InstallScout", "usage-session.json")


def session_id(now: float | None = None) -> str:
    """Return the Aptabase session id, reused for one hour on this PC."""
    current = time.time() if now is None else now
    path = session_path()
    try:
        with open(path, encoding="utf-8") as handle:
            item = json.load(handle)
        last = float(item.get("lastTouched", 0))
        stored = item.get("id")
        if isinstance(stored, str) and stored.isdigit() and current - last < SESSION_SECONDS:
            try:
                with open(path, "w", encoding="utf-8") as handle:
                    json.dump({"id": stored, "lastTouched": current}, handle)
            except OSError:
                pass
            return stored
    except (OSError, ValueError, TypeError):
        pass
    epoch = str(int(current))
    random = str(int.from_bytes(os.urandom(4), "big") % 100_000_000).zfill(8)
    fresh = epoch + random
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump({"id": fresh, "lastTouched": current}, handle)
    except OSError:
        pass
    return fresh


def locale_name() -> str:
    try:
        import locale

        chosen = locale.getlocale()[0] or ""
    except Exception:
        chosen = ""
    if not chosen:
        chosen = os.environ.get("LANG", "") or ""
    return chosen.split(".", 1)[0]


def os_facts() -> tuple[str, str]:
    try:
        import platform

        return platform.system(), platform.release()
    except Exception:
        return "", ""


def timestamp() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def build_event(version: str, debug: bool, session: str | None = None) -> dict:
    os_name, os_version = os_facts()
    return {
        "timestamp": timestamp(),
        "sessionId": session or session_id(),
        "eventName": "app_start",
        "systemProps": {
            "locale": locale_name(),
            "osName": os_name,
            "osVersion": os_version,
            "isDebug": bool(debug),
            "appVersion": version,
            "sdkVersion": SDK_VERSION,
        },
        "props": {"source": "program"},
    }


def post_event(event: dict, timeout: float = 2) -> int:
    request = urllib.request.Request(
        EVENT_URL,
        data=json.dumps(event).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "App-Key": APP_KEY,
        },
        method="POST",
    )
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        response.read()
        return int(response.status)


def send_usage(version: str, debug: bool) -> None:
    try:
        post_event(build_event(version, debug))
    except Exception:
        return


def start() -> None:
    version = ""
    frozen = bool(getattr(sys, "frozen", False))
    try:
        import installscout

        version = str(getattr(installscout, "__version__", ""))
    except Exception:
        version = ""
    debug = os.environ.get("INSTALLSCOUT_USAGE_DEBUG") == "1" or not frozen
    threading.Thread(
        target=send_usage,
        args=(version, debug),
        name="installscout-usage",
        daemon=False,
    ).start()
    from installscout.cli import run_cli

    raise SystemExit(run_cli())


if __name__ == "__main__":
    start()
