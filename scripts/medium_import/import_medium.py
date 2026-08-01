#!/usr/bin/env python3
"""Import Medium articles from RSS or a URL list into Quarto posts."""

from __future__ import annotations

import argparse
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSTS = ROOT / "posts"
ARTICLES_FILE = Path(__file__).with_name("articles.txt")
UA = "Mozilla/5.0"


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s[:60].rstrip("-")


def fetch(url: str) -> str:
    jina = f"https://r.jina.ai/{url.split('?')[0]}"
    req = urllib.request.Request(jina, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_jina(md: str) -> tuple[str, str, str]:
    title = ""
    date = ""
    m = re.search(r"^Title:\s*(.+)$", md, re.M)
    if m:
        title = m.group(1).strip()
    m = re.search(r"^Published Time:\s*(.+)$", md, re.M)
    if m:
        try:
            date = parsedate_to_datetime(m.group(1).strip()).strftime("%Y-%m-%d")
        except Exception:
            date = m.group(1).strip()[:10]
    m = re.search(r"Markdown Content:\s*\n", md)
    body = md[m.end() :] if m else md
    return title, date, body.strip()


def clean_body(body: str) -> str:
  lines = body.splitlines()
  out: list[str] = []
  skip_patterns = (
    "Sign up",
    "Get app",
    "Subscribe",
    "Remember me for faster sign in",
    "Press enter or click to view image in full size",
    "Written by Muhammet",
    "Published in ",
    "See all from",
    "Recommended from Medium",
    "No responses yet",
    "Responses (",
    "Join Medium for free",
    "--",
    "Share",
  )
  medium_tags = {
    "ChatGPT", "Streamlit", "Langchain", "LLM", "OpenAI", "Cybersecurity",
    "Machine Learning", "AI", "MLOps", "NLP", "Deep Learning",
  }
  in_footer = False
  in_inbox = False
  for line in lines:
    stripped = line.strip()
    if stripped.startswith("## Get Muhammet") or stripped.startswith("## Get stories"):
      in_inbox = True
      continue
    if in_inbox:
      if stripped.startswith("## ") and "inbox" not in stripped.lower():
        in_inbox = False
      else:
        continue
    if re.match(r"^\d+ min read$", stripped):
      continue
    if re.match(
      r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4}$",
      stripped,
    ):
      continue
    if stripped.startswith("## Written by") or stripped.startswith("## More from"):
      in_footer = True
    if in_footer:
      continue
    if stripped.startswith("[![") and "medium.com" in stripped:
      continue
    if any(stripped == p or stripped.startswith(p) for p in skip_patterns):
      continue
    if not out and stripped in medium_tags:
      continue
    if re.match(r"^!\[Image \d+\]", stripped) and "miro.medium.com" not in stripped:
      continue
    # drop lone tag lines at end
    if re.match(r"^[A-Z][a-z]+(?: [A-Z][a-z]+)*$", stripped) and len(stripped) < 40:
      if out and out[-1].strip() == "":
        continue
    out.append(line)
  text = "\n".join(out).strip()
  # fix code blocks: jina sometimes merges code on one line after ```
  text = re.sub(r"```(\w*)\n([^`]+?)```", _fix_codeblock, text, flags=re.S)
  text = re.sub(
    r'os\.environ\["OPENAI_API_KEY"\]\s*=\s*"[^"]*"',
    'os.environ["OPENAI_API_KEY"] = "<YOUR_OPENAI_API_KEY>"',
    text,
  )
  text = re.sub(r"\n{3,}", "\n\n", text)
  return text


def _fix_codeblock(match: re.Match[str]) -> str:
    lang = match.group(1) or "python"
    code = match.group(2)
    # insert newlines before common keywords if squashed
    if "\n" not in code.strip() and len(code) > 80:
        code = re.sub(r"(?<=[;}])(?=\s*(?:from|import|def|class|if|for|with|return))", "\n", code)
    return f"```{lang}\n{code.strip()}\n```"


def categories_for(title: str, body: str) -> list[str]:
    t = (title + body).lower()
    cats = ["ml"]
    if any(k in t for k in ("mlflow", "docker", "gcp", "vertex", "keras", "devops", "kafka")):
        cats.append("mlops")
    if any(k in t for k in ("langchain", "streamlit", "llm", "chatgpt", "rag")):
        cats.append("llm")
    if any(
        k in t
        for k in (
            "security",
            "backdoor",
            "evasion",
            "cyber",
            "solid",
            "design by contract",
            "defensive programming",
            "fastapi",
            "mongodb",
        )
    ):
        cats.append("software")
    if "career" in t:
        cats.append("academy")
    if "review" in t or "technical debt" in t:
        cats.append("software")
    return sorted(set(cats))


def load_articles(path: Path = ARTICLES_FILE) -> list[tuple[str, str]]:
    """Load ``slug|url`` pairs from the articles manifest."""
    articles: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        slug, url = line.split("|", 1)
        articles.append((slug.strip(), url.strip().split("?")[0]))
    return articles


def import_article(url: str, slug: str | None = None, *, force: bool = False) -> None:
    """Fetch one Medium article and write or refresh its Quarto post."""
    url = url.split("?")[0]
    post_dir = POSTS / slug if slug else None

    print(f"Fetching: {url}")
    raw = fetch(url)
    title, date, body = parse_jina(raw)
    if not title:
        raise ValueError(f"could not parse title from {url}")
    body = clean_body(body)
    if len(body) < 200:
        print(f"  WARN: short body ({len(body)} chars) for {title}")
    resolved_slug = slug or slugify(title)
    post_dir = POSTS / resolved_slug
    if post_dir.exists():
        if not force:
            print(f"  SKIP dir exists: {resolved_slug}")
            return
        for img in post_dir.glob("img_*"):
            img.unlink()
    else:
        post_dir.mkdir(parents=True, exist_ok=True)
    cats = categories_for(title, body)
    write_post(resolved_slug, title, date, body, cats, medium_url=url)


def download_images(body: str, dest_dir: Path) -> str:
    dest_dir.mkdir(parents=True, exist_ok=True)
    idx = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal idx
        alt = match.group(1)
        url = match.group(2)
        if "miro.medium.com" not in url and "cdn-images" not in url:
          return match.group(0)
        ext = ".png" if ".png" in url else ".jpg"
        fname = f"img_{idx}{ext}"
        idx += 1
        path = dest_dir / fname
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                path.write_bytes(r.read())
            return f"![{alt}]({fname})"
        except Exception:
            return match.group(0)

    return re.sub(r"!\[([^\]]*)\]\((https?://[^)]+)\)", repl, body)


def write_post(
    slug: str,
    title: str,
    date: str,
    body: str,
    cats: list[str],
    *,
    medium_url: str = "",
) -> None:
    post_dir = POSTS / slug
    post_dir.mkdir(parents=True, exist_ok=True)
    body = download_images(body, post_dir)
    image_line = ""
    imgs = sorted(post_dir.glob("img_*"))
    if imgs:
        image_line = f'image: "{imgs[0].name}"\n'
    cats_str = ", ".join(cats)
    medium_line = f'medium_url: "{medium_url}"\n' if medium_url else ""
    qmd = f"""---
title: "{title.replace('"', '\\"')}"
author: "Nusret Ozates"
date: {date}
categories: [{cats_str}]
{medium_line}{image_line}---

{body}
"""
    (post_dir / "index.qmd").write_text(qmd, encoding="utf-8")
    print(f"Wrote posts/{slug}/index.qmd")


def import_from_manifest(*, force: bool = False) -> None:
    """Import every article listed in ``articles.txt``."""
    articles = load_articles()
    print(f"Importing {len(articles)} articles (force={force})")
    for slug, url in articles:
        try:
            import_article(url, slug, force=force)
        except Exception as err:
            print(f"  ERROR {slug}: {err}")


def import_from_rss() -> None:
    """Import new articles from the Medium RSS feed."""
    feed = urllib.request.urlopen(
        urllib.request.Request("https://medium.com/feed/@m.nusret.ozates", headers={"User-Agent": UA}),
        timeout=60,
    ).read()
    root = ET.fromstring(feed)
    known_urls = {url for _, url in load_articles()}
    for item in root.findall("channel/item"):
        link = (item.findtext("link") or "").split("?")[0]
        if link in known_urls:
            continue
        import_article(link, force=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Medium articles into Quarto posts.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Import all articles from articles.txt",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing post directories",
    )
    parser.add_argument(
        "--rss",
        action="store_true",
        help="Import only new articles from RSS (not in articles.txt)",
    )
    args = parser.parse_args()
    if args.all:
        import_from_manifest(force=args.force)
    elif args.rss:
        import_from_rss()
    else:
        import_from_manifest(force=args.force)


if __name__ == "__main__":
    main()
