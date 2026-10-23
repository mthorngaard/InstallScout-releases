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
LOCALE_LIMIT = 10


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


def shorten_locale(value: str) -> str:
    """Aptabase rejects the whole event when locale is longer than 10 characters."""
    text = value.strip().replace("_", "-")
    text = text.split(".", 1)[0].split("@", 1)[0].strip()
    return text[:LOCALE_LIMIT]


def windows_locale_name() -> str:
    """Return a short Windows locale such as da-DK.

    Python's own name on Windows is English_United States or Danish_Denmark,
    and Aptabase drops the event because that string is longer than 10 characters.
    """
    if os.name != "nt":
        return ""
    try:
        import ctypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetUserDefaultLocaleName.argtypes = [ctypes.c_wchar_p, ctypes.c_int]
        kernel.GetUserDefaultLocaleName.restype = ctypes.c_int
        buffer = ctypes.create_unicode_buffer(85)
        count = kernel.GetUserDefaultLocaleName(buffer, len(buffer))
        if count > 0 and buffer.value:
            return buffer.value
        kernel.GetUserDefaultLCID.restype = ctypes.c_uint
        import locale

        return locale.windows_locale.get(int(kernel.GetUserDefaultLCID()), "")
    except Exception:
        return ""


def locale_name() -> str:
    windows = windows_locale_name()
    if windows:
        return shorten_locale(windows) or "en"
    chosen = ""
    try:
        import locale

        chosen = locale.getlocale()[0] or ""
        if chosen:
            normalized = locale.normalize(chosen.replace(" ", "_"))
            short = normalized.split(".", 1)[0]
            if short:
                return shorten_locale(short) or "en"
    except Exception:
        chosen = ""
    if not chosen:
        chosen = os.environ.get("LANG", "") or os.environ.get("LC_ALL", "") or ""
    return shorten_locale(chosen) or "en"


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


def post_event(event: dict, timeout: float = 12) -> int:
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
