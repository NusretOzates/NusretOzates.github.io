#!/usr/bin/env python3
"""Restore truncated Astro blog posts from a Medium export + GitHub gists."""

from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

EXPORT_POSTS = Path("/tmp/medium-export/posts")
GISTS_DIR = Path("/tmp/medium-export/gists")
LOCAL_POSTS = Path("/workspace/astro-site/src/content/posts")
OUT_PREVIEW = Path("/tmp/medium-export/converted")

LANG_BY_EXT = {
    ".py": "python",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".toml": "toml",
    ".js": "javascript",
    ".ts": "typescript",
    ".sh": "bash",
    ".bash": "bash",
    ".conf": "toml",
    ".json": "json",
    ".md": "markdown",
    ".txt": "",
    ".dockerfile": "dockerfile",
}


def load_gist(gist_id: str) -> str:
    """Return markdown fenced code for a gist id."""
    path = GISTS_DIR / f"{gist_id}.json"
    if not path.exists():
        return f"<!-- missing gist {gist_id} -->\n"
    data = json.loads(path.read_text(encoding="utf-8"))
    parts: list[str] = []
    for name, content in data["files"].items():
        ext = Path(name).suffix.lower()
        lang = LANG_BY_EXT.get(ext, "")
        fence = f"```{lang}".rstrip()
        body = (content or "").rstrip("\n")
        parts.append(f"{fence}\n{body}\n```")
    return "\n\n".join(parts)


def inline_md(el: Tag) -> str:
    """Convert inline HTML to markdown."""
    out: list[str] = []
    for child in el.children:
        if isinstance(child, NavigableString):
            out.append(str(child).replace("\xa0", " "))
            continue
        if not isinstance(child, Tag):
            continue
        name = child.name.lower()
        if name in {"strong", "b"}:
            out.append(f"**{inline_md(child).strip()}**")
        elif name in {"em", "i"}:
            out.append(f"*{inline_md(child).strip()}*")
        elif name == "code":
            out.append(f"`{child.get_text()}`")
        elif name == "a":
            text = inline_md(child).strip() or child.get_text().strip()
            href = child.get("href") or ""
            if href:
                out.append(f"[{text}]({href})")
            else:
                out.append(text)
        elif name == "br":
            out.append("\n")
        else:
            out.append(inline_md(child))
    return "".join(out)


def normalize_ws(text: str) -> str:
    text = text.replace("\xa0", " ").replace("\u200a", " ").replace("\u2009", " ")
    text = text.replace("—", "—").replace("–", "–")
    # Medium soft hyphen / special dashes already fine
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def convert_body(html: str, local_images: list[str]) -> str:
    """Convert Medium export article body to markdown."""
    soup = BeautifulSoup(html, "lxml")
    body = soup.select_one("section.e-content") or soup.select_one("article")
    if body is None:
        raise ValueError("no article body")

    blocks: list[str] = []
    img_i = 0
    title_skipped = False

    # Walk top-level graf elements in document order
    for el in body.find_all(
        ["h2", "h3", "h4", "p", "blockquote", "pre", "figure", "ol", "ul", "hr"],
        recursive=True,
    ):
        # Skip nested list items handled via parent ol/ul
        if el.name in {"li"}:
            continue
        # Avoid processing descendants twice when parent already handled
        parent_graf = el.find_parent(
            ["figure", "blockquote", "pre", "ol", "ul", "h2", "h3", "h4", "p"]
        )
        if parent_graf is not None and parent_graf != el:
            # allow nested only when parent is section wrappers — find_parent hits
            # only those tags; if parent is another content tag, skip
            if parent_graf.name in {"figure", "blockquote", "pre", "ol", "ul"}:
                continue
            if parent_graf.name in {"h2", "h3", "h4", "p"} and el.name not in {
                "figure",
                "pre",
            }:
                continue

        classes = " ".join(el.get("class") or [])

        if el.name in {"h2", "h3", "h4"}:
            text = inline_md(el).strip()
            if not text:
                continue
            # Skip duplicate title heading (first h3 with graf--title)
            if "graf--title" in classes and not title_skipped:
                title_skipped = True
                continue
            level = {"h2": 2, "h3": 2, "h4": 3}[el.name]
            # Medium uses h3 for section titles → ## ; h4 → ###
            if el.name == "h3":
                level = 2
            elif el.name == "h4":
                level = 3
            # Strip bold wrappers around whole heading
            text = re.sub(r"^\*\*(.+)\*\*$", r"\1", text)
            blocks.append("#" * level + " " + text)
            continue

        if el.name == "p":
            text = inline_md(el).strip()
            if text:
                blocks.append(text)
            continue

        if el.name == "blockquote":
            text = inline_md(el).strip()
            if text:
                quoted = "\n".join(f"> {line}" if line else ">" for line in text.splitlines())
                blocks.append(quoted)
            continue

        if el.name == "pre":
            # Medium export uses <br> for newlines inside <pre>
            for br in el.find_all("br"):
                br.replace_with("\n")
            code = el.get_text().replace("\xa0", " ").rstrip("\n")
            lang = ""
            if re.search(r"^\s*(def |import |class |from )", code, re.M):
                lang = "python"
            elif re.search(r"^\s*(FROM |WORKDIR |RUN |COPY |ENTRYPOINT )", code, re.M):
                lang = "dockerfile"
            elif re.search(r"^\s*(version:|services:)", code, re.M):
                lang = "yaml"
            elif re.search(r"^\s*(\[\[|\[)", code):
                lang = "toml"
            elif re.search(
                r"^\s*(docker |sudo |pip |pip3 |mlflow |export |gcloud )",
                code,
                re.M,
            ):
                lang = "bash"
            fence = f"```{lang}".rstrip()
            blocks.append(f"{fence}\n{code}\n```")
            continue

        if el.name in {"ol", "ul"}:
            items = []
            for i, li in enumerate(el.find_all("li", recursive=False), start=1):
                prefix = f"{i}." if el.name == "ol" else "*"
                items.append(f"{prefix} {inline_md(li).strip()}")
            if items:
                blocks.append("\n".join(items))
            continue

        if el.name == "figure":
            script = el.find("script", src=True)
            if script and "gist.github.com" in script["src"]:
                m = re.search(r"gist\.github\.com/[^/]+/([a-f0-9]+)", script["src"])
                if m:
                    blocks.append(load_gist(m.group(1)))
                continue
            img = el.find("img")
            if img:
                alt = (img.get("alt") or "Image").strip() or "Image"
                if img_i < len(local_images):
                    src = local_images[img_i]
                else:
                    src = img.get("src") or ""
                img_i += 1
                blocks.append(f"![{alt}]({src})")
                cap = el.find("figcaption")
                if cap:
                    cap_text = inline_md(cap).strip()
                    if cap_text:
                        blocks.append(cap_text)
            continue

        if el.name == "hr":
            # section dividers — skip
            continue

    md = "\n\n".join(blocks)
    md = normalize_ws(md)
    # Medium often glues <strong> to adjacent words with no spaces
    md = re.sub(r"(\w)\*\*([^*]+?)\*\*(\w)", r"\1 **\2** \3", md)
    md = re.sub(r"(\w)\*\*([^*]+?)\*\*", r"\1 **\2**", md)
    md = re.sub(r"\*\*([^*]+?)\*\*(\w)", r"**\1** \2", md)
    # Space before markdown links glued to a word: by[Name]
    md = re.sub(r"([A-Za-z0-9.,;:])\[", r"\1 [", md)
    md = re.sub(
        r"\n+By \[Muhammet.*$",
        "\n",
        md,
        flags=re.S,
    )
    return md


def extract_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    return "---" + parts[1] + "---\n\n", parts[2]


def local_image_list(post_dir: Path) -> list[str]:
    """Prefer existing local images in img_N order, then other images."""
    imgs = sorted(post_dir.glob("img_*"))
    names = [p.name for p in imgs]
    # Also include non-img_ assets already referenced? Keep simple: only img_*
    return names


def export_id_map() -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for p in EXPORT_POSTS.glob("*.html"):
        m = re.search(r"-([a-f0-9]{10,12})\.html$", p.name)
        if m:
            mapping[m.group(1)] = p
    return mapping


def should_restore(local_words: int, export_words: int, local_fences: int, export_gists: int) -> bool:
    if export_words <= 0:
        return False
    ratio = local_words / export_words
    if ratio < 0.92:
        return True
    if export_gists > 0 and local_fences < export_gists:
        return True
    return False


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def main() -> None:
    OUT_PREVIEW.mkdir(parents=True, exist_ok=True)
    exports = export_id_map()
    restored: list[str] = []
    skipped: list[str] = []

    for post_dir in sorted(LOCAL_POSTS.iterdir()):
        md_path = post_dir / "index.md"
        if not md_path.is_file():
            continue
        raw = md_path.read_text(encoding="utf-8")
        fm, body = extract_frontmatter(raw)
        m = re.search(r'mediumUrl:\s*"([^"]+)"', fm)
        if not m:
            skipped.append(f"{post_dir.name}: no mediumUrl")
            continue
        mid = m.group(1).rstrip("/").rsplit("-", 1)[-1]
        exp = exports.get(mid)
        if not exp:
            skipped.append(f"{post_dir.name}: no export match ({mid})")
            continue

        html = exp.read_text(encoding="utf-8")
        gist_ids = re.findall(r"gist\.github\.com/[^/]+/([a-f0-9]+)", html)
        # rough export word count without scripts
        plain = re.sub(r"<script[\s\S]*?</script>", "", html)
        plain = re.sub(r"<[^>]+>", " ", plain)
        export_words = word_count(plain)
        local_words = word_count(body)
        local_fences = body.count("```") // 2

        if not should_restore(local_words, export_words, local_fences, len(gist_ids)):
            skipped.append(
                f"{post_dir.name}: ok (ratio {local_words/export_words:.2f}, "
                f"fences {local_fences}/{len(gist_ids)})"
            )
            continue

        images = local_image_list(post_dir)
        new_body = convert_body(html, images)
        preview = OUT_PREVIEW / f"{post_dir.name}.md"
        preview.write_text(new_body, encoding="utf-8")

        # Keep frontmatter; replace body
        md_path.write_text(fm + new_body, encoding="utf-8")
        restored.append(
            f"{post_dir.name}: {local_words}->{word_count(new_body)} words, "
            f"fences {local_fences}->{new_body.count('```')//2}, gists {len(gist_ids)}"
        )

    print("=== RESTORED ===")
    for line in restored:
        print(line)
    print("\n=== SKIPPED ===")
    for line in skipped:
        print(line)
    print(f"\nRestored {len(restored)} posts")


if __name__ == "__main__":
    main()
