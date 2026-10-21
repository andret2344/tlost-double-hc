"""Checks that the mod is in a releasable state: metadata.xml is valid and matches main.lua,
and no in-game test values are left in the config constants."""

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

errors = []

try:
    metadata = ET.parse(ROOT / "metadata.xml").getroot()
except ET.ParseError as e:
    sys.exit(f"metadata.xml is not valid XML: {e}")

for field in ("name", "directory", "version"):
    if not (metadata.findtext(field) or "").strip():
        errors.append(f"metadata.xml: <{field}> is missing or empty")

main_lua = (ROOT / "main.lua").read_text(encoding="utf-8")

registered = re.search(r'RegisterMod\(\s*"([^"]+)"', main_lua)
metadata_name = (metadata.findtext("name") or "").strip()
if not registered:
    errors.append('main.lua: no RegisterMod("...") call found')
elif registered.group(1) != metadata_name:
    errors.append(
        f'name mismatch: RegisterMod("{registered.group(1)}") vs <name>{metadata_name}</name>'
    )

if re.search(r"^local DEBUG\s*=\s*true\b", main_lua, re.MULTILINE):
    errors.append("main.lua: DEBUG is true (test value)")

if re.search(r"^local HOLY_CARD_CHANCE\s*=\s*1(\.0*)?\s*(--.*)?$", main_lua, re.MULTILINE):
    errors.append("main.lua: HOLY_CARD_CHANCE is 1 (test value)")

for error in errors:
    print(f"::error::{error}")

if errors:
    sys.exit(1)

print("Mod metadata and config are OK.")
