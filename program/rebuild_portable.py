"""Build a portable InstallScout exe that sends an anonymous app_start.

The published program is a PyInstaller archive. This replaces its startup
script and moves the version string from 1.8.63 to 1.8.64. The rest of the
program is unchanged.

Requires CPython 3.14.6, the same interpreter the portable exe was frozen with.
"""

from __future__ import annotations

import argparse
import marshal
import struct
import sys
import zlib
from pathlib import Path

COOKIE_MAGIC = b"MEI\014\013\012\013\016"
COOKIE_SIZE = 88
COOKIE_STRUCT = "!8sIIii64s"
TOC_HEAD = "!IIIBc"
OLD_VERSION = "1.8.63"
NEW_VERSION = "1.8.64"


def _require_python() -> None:
    if sys.version_info[:3] != (3, 14, 6):
        raise SystemExit("Rebuild with CPython 3.14.6 so the frozen exe can load the new startup script.")


def _cookie(data: bytes) -> tuple[int, int, int, int, bytes]:
    cookie_at = data.rfind(COOKIE_MAGIC)
    if cookie_at < 0 or cookie_at + COOKIE_SIZE != len(data):
        raise SystemExit("The file is not a PyInstaller 2.1+ archive ending at the cookie.")
    magic, length, toc, toc_len, pyver, pylib = struct.unpack(COOKIE_STRUCT, data[cookie_at : cookie_at + COOKIE_SIZE])
    if magic != COOKIE_MAGIC or pyver != 314:
        raise SystemExit("Unexpected PyInstaller cookie.")
    overlay = len(data) - length
    if overlay < 0:
        raise SystemExit("Archive length points outside the file.")
    return overlay, toc, toc_len, cookie_at, pylib


def _parse_toc(data: bytes, overlay: int, toc: int, toc_len: int) -> list[dict]:
    pos = overlay + toc
    end = pos + toc_len
    fixed = struct.calcsize(TOC_HEAD)
    entries = []
    while pos < end:
        entry_size = struct.unpack("!i", data[pos : pos + 4])[0]
        if entry_size < 4 + fixed or pos + entry_size > end:
            raise SystemExit("Broken archive table of contents.")
        body = data[pos + 4 : pos + entry_size]
        entry_pos, cmprsd, uncmpr, flag, kind, name_raw = struct.unpack(f"!IIIBc{entry_size - 4 - fixed}s", body)
        entries.append(
            {
                "pos": entry_pos,
                "cmprsd": cmprsd,
                "uncmpr": uncmpr,
                "flag": flag,
                "kind": kind,
                "name_raw": name_raw,
                "name": name_raw.decode("utf-8").rstrip("\0"),
            }
        )
        pos += entry_size
    return entries


def _entry_bytes(data: bytes, overlay: int, entry: dict) -> bytes:
    start = overlay + entry["pos"]
    blob = data[start : start + entry["cmprsd"]]
    if entry["flag"] == 1:
        blob = zlib.decompress(blob)
        if len(blob) != entry["uncmpr"]:
            raise SystemExit(f"Compressed size mismatch for {entry['name']}.")
    return blob


def _startup_blob(source: Path) -> bytes:
    code = compile(source.read_text(encoding="utf-8"), "app.py", "exec")
    return marshal.dumps(code)


def _bump_version(pyz: bytes) -> bytes:
    if pyz[:4] != b"PYZ\x00":
        raise SystemExit("PYZ archive is missing.")
    toc_pos = struct.unpack("!i", pyz[8:12])[0]
    toc = marshal.loads(pyz[toc_pos:])
    if not isinstance(toc, list):
        raise SystemExit("Unexpected PYZ table.")
    extra = bytearray()
    updated = []
    found = False
    for key, val in toc:
        ispkg, pos, length = val
        if key == "installscout" and ispkg == 1:
            code = marshal.loads(zlib.decompress(pyz[pos : pos + length]))
            if OLD_VERSION not in code.co_consts:
                raise SystemExit("Could not find version 1.8.63 in the program.")
            consts = tuple(NEW_VERSION if item == OLD_VERSION else item for item in code.co_consts)
            code = code.replace(co_consts=consts)
            compressed = zlib.compress(marshal.dumps(code))
            updated.append((key, (ispkg, toc_pos + len(extra), len(compressed))))
            extra += compressed
            found = True
        else:
            updated.append((key, val))
    if not found:
        raise SystemExit("installscout package is missing from the archive.")
    out = bytearray(pyz[:toc_pos] + extra + marshal.dumps(updated))
    struct.pack_into("!i", out, 8, toc_pos + len(extra))
    return bytes(out)


def _pack_toc(entries: list[dict]) -> bytes:
    fixed = struct.calcsize(TOC_HEAD)
    out = bytearray()
    for entry in entries:
        body = struct.pack(
            TOC_HEAD,
            entry["pos"],
            entry["cmprsd"],
            entry["uncmpr"],
            entry["flag"],
            entry["kind"],
        ) + entry["name_raw"]
        out += struct.pack("!i", 4 + len(body))
        if len(body) != fixed + len(entry["name_raw"]):
            raise SystemExit("Table entry size drifted.")
        out += body
    return bytes(out)


def rebuild(source_exe: Path, dest_exe: Path, startup: Path) -> None:
    _require_python()
    data = source_exe.read_bytes()
    overlay, toc, toc_len, _cookie_at, pylib = _cookie(data)
    entries = _parse_toc(data, overlay, toc, toc_len)
    startup_blob = _startup_blob(startup)
    payload = bytearray()
    rewritten = []
    for entry in entries:
        if entry["name"] == "app" and entry["kind"] == b"s":
            raw = startup_blob
            stored = zlib.compress(raw)
            flag = 1
        elif entry["name"] == "PYZ.pyz" and entry["kind"] == b"z":
            raw = _bump_version(_entry_bytes(data, overlay, entry))
            stored = raw
            flag = 0
        else:
            start = overlay + entry["pos"]
            stored = data[start : start + entry["cmprsd"]]
            raw = b""
            flag = entry["flag"]
        item = dict(entry)
        item["pos"] = len(payload)
        item["cmprsd"] = len(stored)
        if entry["name"] in {"app", "PYZ.pyz"}:
            item["uncmpr"] = len(raw)
        item["flag"] = flag
        rewritten.append(item)
        payload += stored
    table = _pack_toc(rewritten)
    length = len(payload) + len(table) + COOKIE_SIZE
    cookie = struct.pack(COOKIE_STRUCT, COOKIE_MAGIC, length, len(payload), len(table), 314, pylib)
    dest_exe.write_bytes(data[:overlay] + payload + table + cookie)
    _verify(dest_exe)


def _verify(dest_exe: Path) -> None:
    data = dest_exe.read_bytes()
    overlay, toc, toc_len, _cookie_at, _pylib = _cookie(data)
    entries = _parse_toc(data, overlay, toc, toc_len)
    for entry in entries:
        if entry["flag"] == 1:
            raw = _entry_bytes(data, overlay, entry)
            if len(raw) != entry["uncmpr"]:
                raise SystemExit(f"Size check failed for {entry['name']}.")
    app = next(entry for entry in entries if entry["name"] == "app")
    startup = _entry_bytes(data, overlay, app)
    code = marshal.loads(startup)
    consts = _consts(code)
    if "https://eu.aptabase.com/api/v0/event" not in consts:
        raise SystemExit("Rebuilt startup script is missing the Aptabase address.")
    if "app_start" not in consts:
        raise SystemExit("Rebuilt startup script is missing app_start.")
    pyz = _entry_bytes(data, overlay, next(entry for entry in entries if entry["name"] == "PYZ.pyz"))
    toc_pos = struct.unpack("!i", pyz[8:12])[0]
    for key, val in marshal.loads(pyz[toc_pos:]):
        ispkg, pos, length = val
        if key == "installscout" and ispkg == 1:
            package = marshal.loads(zlib.decompress(pyz[pos : pos + length]))
            if NEW_VERSION not in package.co_consts or OLD_VERSION in package.co_consts:
                raise SystemExit("Version was not updated to 1.8.64.")
            return
    raise SystemExit("Could not verify the installscout package.")


def _consts(code) -> set[str]:
    found = set()
    for item in code.co_consts:
        if isinstance(item, str):
            found.add(item)
        elif hasattr(item, "co_consts"):
            found.update(_consts(item))
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description="Build InstallScout portable exe with anonymous usage.")
    parser.add_argument("source_exe", type=Path)
    parser.add_argument("dest_exe", type=Path)
    parser.add_argument("--startup", type=Path, default=Path(__file__).with_name("app.py"))
    args = parser.parse_args()
    rebuild(args.source_exe, args.dest_exe, args.startup)
    print(f"Wrote {args.dest_exe}")


if __name__ == "__main__":
    main()
