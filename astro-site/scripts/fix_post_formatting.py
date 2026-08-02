#!/usr/bin/env python3
"""Fix common markdown formatting issues introduced during Quarto migration."""

from __future__ import annotations

import re
from pathlib import Path

POSTS_DIR = Path(__file__).resolve().parents[1] / "src" / "content" / "posts"


def fix_bold_spacing(text: str) -> str:
    """Remove stray spaces inside **bold** markers."""
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"\*\* +([^*]+?) +\*\*", r"**\1**", text)
        text = re.sub(r"\*\* +([^*]+?)\*\*", r"**\1**", text)
        text = re.sub(r"\*\*([^*]+?) +\*\*", r"**\1**", text)
    return text


def fix_escaped_underscores(text: str) -> str:
    """Turn Quarto-style \\_ into _ outside code fences."""
    parts = re.split(r"(```[\s\S]*?```)", text)
    out: list[str] = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(part)
        else:
            out.append(part.replace("\\_", "_"))
    return "".join(out)


def fix_code_fence_spacing(text: str) -> str:
    """Remove blank lines inside fenced code blocks."""
    def _clean_block(match: re.Match[str]) -> str:
        fence = match.group(1)
        lang = match.group(2) or ""
        body = match.group(3)
        lines = body.split("\n")
        cleaned = [line for line in lines if line.strip() != ""]
        if not cleaned:
            return match.group(0)
        return f"{fence}{lang}\n" + "\n".join(cleaned) + f"\n{fence}"

    return re.sub(
        r"(```+)(\w*)\n([\s\S]*?)\n```+",
        _clean_block,
        text,
    )


def fix_bracket_spacing_in_code(text: str) -> str:
    """Fix `data ['key']` -> `data['key']` inside code fences."""
    def _fix_block(match: re.Match[str]) -> str:
        block = match.group(0)
        block = re.sub(r"(\w) \[", r"\1[", block)
        block = re.sub(r"\] \(", r"] (", block)
        return block

    return re.sub(r"```[\s\S]*?```", _fix_block, text)


def fix_heading_bold(text: str) -> str:
    return re.sub(r"^## \*\*([^*]+)\*\*\s*$", r"## \1", text, flags=re.MULTILINE)


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = original
    updated = fix_escaped_underscores(updated)
    updated = fix_bold_spacing(updated)
    updated = fix_code_fence_spacing(updated)
    updated = fix_bracket_spacing_in_code(updated)
    updated = fix_heading_bold(updated)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = [p for p in sorted(POSTS_DIR.glob("*/index.md")) if process_file(p)]
    print(f"Updated {len(changed)} posts:")
    for p in changed:
        print(f"  - {p.parent.name}")


if __name__ == "__main__":
    main()
