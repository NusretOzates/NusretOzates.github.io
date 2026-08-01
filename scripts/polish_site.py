#!/usr/bin/env python3
"""Polish imported posts: local Medium links, attribution footer, listing images."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"
PROFILE = ROOT / "profile.jpeg"

FOOTER_MARKER = "medium-attribution"
FOOTER_TEMPLATE = """

::: {{.{marker}}}
Originally published on [Medium]({{{{< meta medium_url >}}}}).
:::
"""


def parse_frontmatter(text: str) -> tuple[str, str, str]:
    """Return prefix, body, medium_url."""
    if not text.startswith("---"):
        return "", text, ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text, ""
    fm, body = parts[1], parts[2]
    match = re.search(r'^medium_url:\s*"([^"]+)"', fm, re.M)
    medium_url = match.group(1) if match else ""
    return f"---{fm}---", body, medium_url


def build_medium_maps() -> tuple[dict[str, str], dict[str, str]]:
    """Map Medium URLs and article-id suffixes to post slugs."""
    by_url: dict[str, str] = {}
    by_id: dict[str, str] = {}
    for qmd in POSTS.glob("*/index.qmd"):
        slug = qmd.parent.name
        _, _, medium_url = parse_frontmatter(qmd.read_text(encoding="utf-8"))
        if not medium_url:
            continue
        clean = medium_url.split("?")[0].rstrip("/")
        by_url[clean] = slug
        article_id = clean.split("-")[-1]
        if len(article_id) >= 8:
            by_id[article_id] = slug
    return by_url, by_id


def local_path(slug: str) -> str:
    return f"/posts/{slug}/"


def replace_medium_links(body: str, by_url: dict[str, str], by_id: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        url = match.group(0).rstrip("/")
        if url in by_url:
            return local_path(by_url[url])
        article_id = url.split("-")[-1]
        if article_id in by_id:
            return local_path(by_id[article_id])
        return match.group(0)

    return re.sub(r"https://medium\.com/[^\s\"')\]]+", repl, body)


def ensure_footer(body: str, medium_url: str) -> str:
    if FOOTER_MARKER in body or not medium_url:
        return body
    footer = FOOTER_TEMPLATE.format(marker=FOOTER_MARKER)
    if "\n## References" in body:
        head, tail = body.split("\n## References", 1)
        return f"{head.rstrip()}{footer}\n\n## References{tail}"
    return f"{body.rstrip()}{footer}\n"


def strip_setext_separator(body: str) -> str:
    """Remove bare --- before attribution; Pandoc treats it as a setext H2."""
    return re.sub(
        r"\n---\n\n(::: \{\.medium-attribution\})",
        r"\n\n\1",
        body,
    )


def reposition_footer(body: str) -> str:
    """Move medium attribution block to the end of the post body."""
    pattern = re.compile(r"\n(?:---\n\n)?::: \{\.medium-attribution\}.*?:::\n*", re.S)
    match = pattern.search(body)
    if not match:
        return body
    footer = re.sub(r"^\n---\n\n", "\n\n", match.group(0))
    body = pattern.sub("\n", body, count=1)
    return strip_setext_separator(body.rstrip() + footer)


def polish_posts() -> None:
    by_url, by_id = build_medium_maps()
    replaced = 0
    footers = 0
    for qmd in sorted(POSTS.glob("*/index.qmd")):
        text = qmd.read_text(encoding="utf-8")
        prefix, body, medium_url = parse_frontmatter(text)
        if not prefix:
            continue
        new_body = replace_medium_links(body, by_url, by_id)
        if new_body != body:
            replaced += 1
        new_body = ensure_footer(new_body, medium_url)
        new_body = reposition_footer(new_body)
        new_body = strip_setext_separator(new_body)
        if FOOTER_MARKER not in body and FOOTER_MARKER in new_body:
            footers += 1
        qmd.write_text(f"{prefix}{new_body}", encoding="utf-8")
    print(f"Updated links in {replaced} posts, added footers to {footers} posts.")


def add_listing_images() -> None:
    bert = POSTS / "bert" / "index.qmd"
    bert_text = bert.read_text(encoding="utf-8")
    if 'image: "masked.png"' not in bert_text:
        bert_text = bert_text.replace(
            'medium_url: "https://medium.com/carbon-consulting/bert-encoder-stack-is-all-you-need-f1483cfe2e07"\n',
            'medium_url: "https://medium.com/carbon-consulting/bert-encoder-stack-is-all-you-need-f1483cfe2e07"\nimage: "masked.png"\n',
        )
        bert.write_text(bert_text, encoding="utf-8")
        print("Added listing image to bert.")

    career_dir = POSTS / "my-2-years-machine-learning-career-story"
    career_img = career_dir / "img_0.jpg"
    if not career_img.exists() and PROFILE.exists():
        shutil.copy2(PROFILE, career_img)
    career = career_dir / "index.qmd"
    career_text = career.read_text(encoding="utf-8")
    if 'image: "img_0.jpg"' not in career_text:
        career_text = career_text.replace(
            'medium_url: "https://medium.com/@m.nusret.ozates/my-2-years-machine-learning-career-story-aefa102e2f73"\n',
            'medium_url: "https://medium.com/@m.nusret.ozates/my-2-years-machine-learning-career-story-aefa102e2f73"\nimage: "img_0.jpg"\n',
        )
        career.write_text(career_text, encoding="utf-8")
        print("Added listing image to career story.")


def main() -> None:
    polish_posts()
    add_listing_images()


if __name__ == "__main__":
    main()
