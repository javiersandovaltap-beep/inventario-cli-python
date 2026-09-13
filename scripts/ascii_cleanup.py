"""ASCII cleanup script for inventario-cli-python governance files.

Replaces non-ASCII characters in the governance files with ASCII equivalents.
Idempotent: running it twice produces no changes the second time.

Run from project root:  python scripts/ascii_cleanup.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# String-level replacements applied BEFORE character-level mapping.
# These handle multi-char emojis that are redundant when paired with a word
# (e.g. "red-circle Blocking" -> "[BLK]", "green-check Allow" -> "Allow").
STRING_MAP: list[tuple[str, str]] = [
    # Severity table in AGENTS.md section 6: emoji + word -> tag only
    ("\U0001f534 Blocking", "[BLK]"),  # red circle + "Blocking"
    ("\U0001f7e1 Required", "[REQ]"),  # yellow circle + "Required"
    # Permission table in AGENTS.md section 9: emoji + word -> word only
    ("\u2705 Allow", "Allow"),  # green check + "Allow"
    ("\u274c Deny", "Deny"),  # red X + "Deny"
    ("\u26a0\ufe0f Ask", "Ask"),  # warning + VS16 + "Ask"
    ("\u26a0 Ask", "Ask"),  # warning + "Ask" (no VS16, just in case)
    # Section sign followed by digit -> "section <digit>"
    ("\u00a7", "section_"),  # placeholder; regex below fixes spacing
]

# Regex patterns applied after STRING_MAP for fine-grained fixes.
REGEX_MAP: list[tuple[re.Pattern[str], str]] = [
    # "section_3" -> "section 3"  (handles section sign followed by digit)
    (re.compile(r"section_(\d)"), r"section \1"),
    # "section_" at end of token (no digit) -> "section"
    (re.compile(r"section_(?=\s|$)"), "section"),
]

# Character-by-character replacements (safe, context-independent).
CHAR_MAP: dict[str, str] = {
    # Dashes
    "\u2014": "--",  # em-dash
    "\u2013": "-",  # en-dash
    # Math operators
    "\u2265": ">=",  # >=
    "\u2264": "<=",  # <=
    "\u2260": "!=",  # !=
    # Arrows
    "\u2192": "->",  # right arrow
    "\u2190": "<-",  # left arrow
    "\u2191": "^",  # up arrow
    "\u2193": "v",  # down arrow
    # Quotes
    "\u201c": '"',  # left double quote
    "\u201d": '"',  # right double quote
    "\u2018": "'",  # left single quote
    "\u2019": "'",  # right single quote
    # Ellipsis
    "\u2026": "...",
    # Spanish accents (lowercase)
    "\u00e1": "a",  # a
    "\u00e9": "e",  # e
    "\u00ed": "i",  # i
    "\u00f3": "o",  # o
    "\u00fa": "u",  # u
    "\u00f1": "n",  # n
    # Spanish accents (uppercase)
    "\u00c1": "A",
    "\u00c9": "E",
    "\u00cd": "I",
    "\u00d3": "O",
    "\u00da": "U",
    "\u00d1": "N",
    # Box-drawing chars (single-line)
    "\u250c": "+",  # top-left corner
    "\u252c": "+",  # top T
    "\u2510": "+",  # top-right corner
    "\u251c": "+",  # left T
    "\u253c": "+",  # cross
    "\u2524": "+",  # right T
    "\u2514": "+",  # bottom-left corner
    "\u2534": "+",  # bottom T
    "\u2518": "+",  # bottom-right corner
    "\u2500": "-",  # horizontal line
    "\u2502": "|",  # vertical line
    # Box-drawing chars (double-line, just in case)
    "\u2554": "+",
    "\u2557": "+",
    "\u255a": "+",
    "\u255d": "+",
    "\u2550": "=",
    "\u2551": "|",
    # Variation selector (invisible emoji modifier, just drop it).
    # Any emoji that survived STRING_MAP as a lone char drops its VS16 here.
    "\ufe0f": "",
    # Severity / status emojis (lone survivors; STRING_MAP handles the
    # "emoji + word" combos above).
    "\U0001f534": "[BLK]",  # red circle
    "\U0001f7e1": "[REQ]",  # yellow circle
    "\u2705": "Yes",  # green check
    "\u274c": "No",  # red X
    "\u26a0": "[!]",  # warning sign
}

TARGET_FILES: list[str] = [
    "CLAUDE.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    ".claude/agents/quick-explorer.md",
    ".claude/agents/implementer.md",
    ".claude/agents/code-reviewer.md",
    ".claude/agents/architecture-reviewer.md",
    ".claude/hooks/block-rm.ps1",
    ".claude/hooks/run-tests.ps1",
    ".claude/settings.json",
    # Local state files (English, model-consumed, gitignored but ASCII-clean)
    ".claude/local/sessionstate.md",
    ".claude/local/memory.md",
]


def find_non_ascii(text: str) -> list[tuple[int, str]]:
    """Return list of (line_number, char) for non-ASCII chars found."""
    findings: list[tuple[int, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for ch in line:
            if ord(ch) > 127:
                findings.append((lineno, ch))
    return findings


def replace_chars(text: str) -> tuple[str, int]:
    """Apply STRING_MAP, then REGEX_MAP, then CHAR_MAP.

    Return (new_text, total_replacement_count).
    """
    count = 0

    # Pass 1: string-level replacements (multi-char emojis + words).
    for old, new in STRING_MAP:
        n = text.count(old)
        if n:
            text = text.replace(old, new)
            count += n

    # Pass 2: regex post-processing (fix spacing for section sign, etc.).
    for pattern, repl in REGEX_MAP:
        text, n = pattern.subn(repl, text)
        count += n

    # Pass 3: character-level replacements (remaining non-ASCII chars).
    out = []
    for ch in text:
        if ch in CHAR_MAP:
            out.append(CHAR_MAP[ch])
            count += 1
        else:
            out.append(ch)
    return "".join(out), count


def process_file(path: Path, dry_run: bool = False) -> dict[str, object]:
    """Process a single file. Returns a report dict."""
    if not path.exists():
        return {"file": str(path), "status": "missing"}

    original = path.read_text(encoding="utf-8")
    before_findings = find_non_ascii(original)
    if not before_findings:
        return {"file": str(path), "status": "clean", "before": 0, "after": 0}

    cleaned, replacements = replace_chars(original)
    after_findings = find_non_ascii(cleaned)

    if not dry_run:
        path.write_text(cleaned, encoding="utf-8")

    # Report unique unknown chars (still non-ASCII after mapping)
    unknown_chars = sorted({ch for _, ch in after_findings})

    return {
        "file": str(path),
        "status": "modified" if not dry_run else "dry-run",
        "before": len(before_findings),
        "after": len(after_findings),
        "replacements": replacements,
        "unknown_chars": unknown_chars,
    }


def main() -> int:
    """Run the ASCII cleanup on all target files.

    Returns 0 if all files are ASCII-clean after processing, 1 if any
    non-ASCII characters remained unmapped (extending CHAR_MAP needed).
    """
    dry_run = "--dry-run" in sys.argv
    project_root = Path.cwd()
    reports = []

    print(f"ASCII cleanup -- project root: {project_root}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'APPLY'}")
    print(f"Target files: {len(TARGET_FILES)}")
    print("-" * 60)

    for rel_path in TARGET_FILES:
        path = project_root / rel_path
        report = process_file(path, dry_run=dry_run)
        reports.append(report)

        status = report["status"]
        if status == "missing":
            print(f"  SKIP   {rel_path} (not found)")
        elif status == "clean":
            print(f"  CLEAN  {rel_path} (no non-ASCII)")
        else:
            before = report["before"]
            after = report["after"]
            reps = report["replacements"]
            unknown = report.get("unknown_chars", [])
            marker = "[DRY]" if dry_run else "[OK] "
            print(f"  {marker} {rel_path}: {before} non-ASCII -> {after} ({reps} replacements)")
            if unknown:
                chars_desc = ", ".join(f"U+{ord(c):04X}" for c in unknown)
                print(f"          WARNING: unknown chars remaining: {chars_desc}")

    print("-" * 60)

    total_before = sum(r.get("before", 0) for r in reports)
    total_after = sum(r.get("after", 0) for r in reports)
    total_reps = sum(r.get("replacements", 0) for r in reports)
    print(f"Totals: {total_before} non-ASCII -> {total_after} ({total_reps} replacements)")

    if total_after > 0:
        print("\nWARNING: some non-ASCII characters were not mapped.")
        print("Inspect manually and extend CHAR_MAP if needed.")
        return 1

    print("\nAll target files are now ASCII-clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
