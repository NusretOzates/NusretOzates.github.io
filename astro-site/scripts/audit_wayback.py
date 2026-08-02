#!/usr/bin/env python3
"""Compare local blog posts against Wayback Machine archives."""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

POSTS_DIR = Path(__file__).resolve().parents[1] / "src" / "content" / "posts"
UA = "Mozilla/5.0 (compatible; portfolio-audit/1.0)"


def fetch(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def wayback_snapshot_url(medium_url: str) -> str | None:
    cdx = (
        "https://web.archive.org/cdx/search/cdx"
        f"?url={urllib.parse.quote(medium_url, safe='')}"
        "&output=json&filter=statuscode:200&limit=-5"
    )

    try:
        data = json.loads(fetch(cdx, timeout=20))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None
    if len(data) < 2:
        return None
    # Prefer 2021-2023 snapshots; take last successful
    for row in reversed(data[1:]):
        ts = row[1]
        original = row[2]
        return f"https://web.archive.org/web/{ts}/{original}"
    return None


def extract_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, parts[2]


def stats(text: str) -> dict[str, int]:
    body = re.sub(r"```[\s\S]*?```", "", text)
    body = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    words = len(re.findall(r"\b\w+\b", body))
    return {
        "words": words,
        "code_fences": len(re.findall(r"^```", text, re.MULTILINE)) // 2,
        "headings": len(re.findall(r"^##+ ", text, re.MULTILINE)),
        "images": len(re.findall(r"!\[", text)),
    }


def wayback_stats(html: str) -> dict[str, int]:
    # Strip tags roughly
    text = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.I)
    # Code blocks on medium often in pre or gist
    code_blocks = len(re.findall(r"<pre", text, re.I)) + len(
        re.findall(r"gist\.github", text, re.I)
    )
    plain = re.sub(r"<[^>]+>", " ", text)
    words = len(re.findall(r"\b\w+\b", plain))
    headings = len(re.findall(r"<h[23][^>]*>", text, re.I))
    images = len(re.findall(r"<img ", text, re.I))
    return {
        "words": words,
        "code_fences": code_blocks,
        "headings": headings,
        "images": images,
    }


def main() -> int:
    results: list[dict] = []
    for post_dir in sorted(POSTS_DIR.iterdir()):
        md_path = post_dir / "index.md"
        if not md_path.is_file():
            continue
        raw = md_path.read_text(encoding="utf-8")
        meta, body = extract_frontmatter(raw)
        local = stats(body)
        slug = post_dir.name
        medium_url = meta.get("mediumUrl", "")
        if not medium_url:
            results.append(
                {
                    "slug": slug,
                    "status": "no_medium_url",
                    "local": local,
                }
            )
            continue

        snap = wayback_snapshot_url(medium_url)
        if not snap:
            results.append(
                {
                    "slug": slug,
                    "status": "no_snapshot",
                    "url": medium_url,
                    "local": local,
                }
            )
            time.sleep(0.5)
            continue

        try:
            html = fetch(snap)
            archived = wayback_stats(html)
        except (urllib.error.URLError, TimeoutError) as err:
            results.append(
                {
                    "slug": slug,
                    "status": f"fetch_error: {err}",
                    "url": medium_url,
                    "local": local,
                }
            )
            continue

        word_ratio = local["words"] / max(archived["words"], 1)
        code_gap = archived["code_fences"] - local["code_fences"]
        flag = (
            word_ratio < 0.75
            or code_gap >= 2
            or (archived["code_fences"] >= 3 and local["code_fences"] == 0)
        )
        results.append(
            {
                "slug": slug,
                "status": "flagged" if flag else "ok",
                "snapshot": snap,
                "local": local,
                "archived": archived,
                "word_ratio": round(word_ratio, 2),
                "code_gap": code_gap,
            }
        )
        time.sleep(0.8)

    flagged = [r for r in results if r.get("status") == "flagged"]
    other = [r for r in results if r.get("status") not in ("ok", "flagged")]

    print("=== FLAGGED (likely incomplete) ===")
    for r in flagged:
        print(
            f"{r['slug']}: words {r['local']['words']}/{r['archived']['words']} "
            f"(ratio {r['word_ratio']}), code {r['local']['code_fences']}/"
            f"{r['archived']['code_fences']} (gap {r['code_gap']})"
        )
        print(f"  {r['snapshot']}")

    print("\n=== NO SNAPSHOT / ERROR ===")
    for r in other:
        print(f"{r['slug']}: {r['status']}")

    print("\n=== OK ===")
    for r in results:
        if r.get("status") == "ok":
            print(
                f"{r['slug']}: words ratio {r['word_ratio']}, "
                f"code gap {r['code_gap']}"
            )

    out = POSTS_DIR.parent / "scripts" / "wayback_audit.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
