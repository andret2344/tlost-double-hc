"""Moves the notes under "## Unreleased" in CHANGELOG.md to a "## <version> - <date>" section and
writes them to the given file, for the body of the GitHub release.

Usage: release_notes.py <version> <output file>

When CHANGELOG.md already has a section for the version (e.g. a deleted release is made again),
it is left as it is and that section's notes are written instead."""

import datetime
import re
import sys
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parents[2] / "CHANGELOG.md"

version, output = sys.argv[1], Path(sys.argv[2])
text = CHANGELOG.read_text(encoding="utf-8")


def section_body(header_pattern):
    match = re.search(rf"^{header_pattern}[^\n]*\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return match, (match.group(1).strip() if match else "")


released, notes = section_body(rf"## {re.escape(version)} - ")
if not released:
    unreleased, notes = section_body("## Unreleased")
    if not unreleased:
        sys.exit("::error::CHANGELOG.md has no '## Unreleased' section")
    if not notes:
        sys.exit("::error::There is nothing under Unreleased in CHANGELOG.md")
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    text = (
        text[: unreleased.start()]
        + f"## Unreleased\n\n## {version} - {today}\n\n{notes}\n\n"
        + text[unreleased.end():]
    )
    CHANGELOG.write_text(text.rstrip("\n") + "\n", encoding="utf-8", newline="\n")

output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(notes + "\n", encoding="utf-8")
