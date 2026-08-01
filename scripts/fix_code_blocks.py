#!/usr/bin/env python3
"""Wrap unfenced code sections in Medium-imported posts."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AP = "\u2019"
LDQ = "\u201c"
RDQ = "\u201d"


def fence_block(text: str, start: str, end: str, lang: str) -> str:
    """Wrap lines between start and end markers (exclusive) in a fenced block."""
    if start not in text:
        raise ValueError(f"start marker not found: {start!r}")
    before, rest = text.split(start, 1)
    if end not in rest:
        raise ValueError(f"end marker not found after {start!r}")
    body, after = rest.split(end, 1)
    if body.lstrip().startswith("```"):
        return before + start + body + end + after
    block = body.strip("\n")
    return f"{before}{start}\n\n```{lang}\n{block}\n```\n\n{end}{after}"


def wrap_between(text: str, before: str, after: str, lang: str) -> str:
    """Wrap content between before and after (markers retained)."""
    if before not in text:
        raise ValueError(f"marker missing: {before!r}")
    head, tail = text.split(before, 1)
    if after not in tail:
        raise ValueError(f"end marker missing after {before!r}: {after!r}")
    body, tail = tail.split(after, 1)
    if body.lstrip().startswith("```"):
        return text
    fenced = f"{before}```{lang}\n{body.strip()}\n```\n{after}"
    return head + fenced + tail


def fix_gnn(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"`MessagePassing`class", "`MessagePassing` class", text)
    text = text.replace(
        "`MessagePassing`class:`propagate`",
        "`MessagePassing` class: `propagate`",
    )
    text = text.replace(
        "`message` , `aggregate` and `update`",
        "`message`, `aggregate`, and `update`",
    )
    text = text.replace("categories: [llm, ml]", "categories: [ml, gnn]")
    text = text.replace("![Image 2](img_0.png)", "![GNN message-passing illustration](img_0.png)")
    intro_end = f"below for reference.{AP}\n\n" if f"below for reference.{AP}" in text else "below for reference.\n\n"
    if intro_end not in text:
        intro_end = "below for reference.\n\n"
    head, rest = text.split(intro_end, 1)
    if rest.lstrip().startswith("```"):
        path.write_text(text, encoding="utf-8")
        return
    code, tail = rest.split("\n## References", 1)
    if " and experiment with different message-passing" in code.split("\n", 1)[0]:
        first_line, _, code_only = code.partition("\n")
        head = head + intro_end.rstrip("\n") + first_line + "\n\n"
        code = code_only
    text = f"{head}{intro_end}```python\n{code.strip()}\n```\n\n## References{tail}"
    path.write_text(text, encoding="utf-8")


def fix_mongodb(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace("![Image 2](img_0.png)", "![FastAPI logo](img_0.png)")
    replacements = [
        (
            "This is what we have in mongo_manager.py:\n\n",
            "\n\nIt is a pretty simple class",
            "python",
        ),
        (
            "db/__init__.py is next:\n\n",
            "\n\nThat\u2019s all :) We will use this db object",
            "python",
        ),
        (
            "So, main.py is next!\n\n",
            "\n\nAs you can see from the 3. line",
            "python",
        ),
        (
            "Now time to go to the users.py.\n\n",
            "\n\nI don\u2019t know if it is the magic",
            "python",
        ),
    ]
    for before, after, lang in replacements:
        text = wrap_between(text, before, after, lang)
    path.write_text(text, encoding="utf-8")


def fix_bert(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    marker = "Download the train data first and create a Tensorflow dataset"
    if marker not in text:
        raise ValueError("bert marker missing")
    tail = text.split(marker, 1)[1]
    if tail.lstrip().startswith("```"):
        return
    text = fence_block(text, marker, "\n\nThanks for reading!", "python")
    path.write_text(text, encoding="utf-8")


def fix_solid(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "class SuperClass:\n    def check" in text:
        return
    old = """class SuperClass: def check(name: str)-> str:

 return nameclass SubClass(SuperClass):

 def check(name: dict) -> dict:

 return nameclass AnotherSubclass(SuperClass):

 def check(name: str, surname: str) -> tuple:

 return name, surname"""
    new = """```python
class SuperClass:
    def check(name: str) -> str:
        return name


class SubClass(SuperClass):
    def check(name: dict) -> dict:
        return name


class AnotherSubclass(SuperClass):
    def check(name: str, surname: str) -> tuple:
        return name, surname
```"""
    if old not in text:
        raise ValueError("solid liskov block not found")
    text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def fix_docker(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace("![Image 2](img_0.png)", "![The matrix from Hell diagram](img_0.png)")
    text = re.sub(
        r"The original video that I take notes from :\n\nThere is a Notion version",
        "There is a Notion version",
        text,
    )
    blocks: list[tuple[str, str, str]] = [
        (
            "Then we need to do these steps in a file called Dockerfile.\n\n",
            f"\nLet{AP}s build our Dockerfile and have a docker image!\n\n",
            "dockerfile",
        ),
        (
            f"Let{AP}s build our Dockerfile and have a docker image!\n\n",
            "\n## What is this Dockerfile?",
            "bash",
        ),
        (
            "You can export your Docker Image as a .tar file with this command:\n\n",
            "\nAnd you can easily import it",
            "bash",
        ),
        (
            "And you can easily import it with a very similar command.\n\n",
            "\n### ENTRYPOINT VS CMD",
            "bash",
        ),
        (
            f"The docker file would be like this:\n\n",
            "\nWhen I run the command:",
            "dockerfile",
        ),
        (
            "When I run the command:\n\n",
            "\nThis CMD command",
            "bash",
        ),
        (
            "To do this we change the dockerfile like this:\n\n",
            "\nThis time when I run:",
            "dockerfile",
        ),
        (
            "This time when I run:\n\n",
            f"\nThe {LDQ}10{RDQ} will be appended",
            "bash",
        ),
        (
            f"But what if I don{AP}t write any number? How can I add a default sleep time?\n\n",
            "\n## **Docker Networking**",
            "dockerfile",
        ),
        (
            "What you would do without docker-compose:\n\n",
            f"\nWith docker-compose, docker-compose.yml:",
            "bash",
        ),
        (
            f"With docker-compose, docker-compose.yml:\n\n",
            "\nAnd run the command:",
            "yaml",
        ),
        (
            "And run the command:\n\n",
            "\nWhat if some of the images",
            "bash",
        ),
        (
            "Change this code:\n\n",
            "\nTo this code:",
            "yaml",
        ),
        (
            "To this code:\n\n",
            "\n## Docker Compose Versions",
            "yaml",
        ),
        (
            "This is the .yaml file you need to write:\n\n",
            f"\nSo, that{AP}s it!",
            "yaml",
        ),
    ]
    for before, after, lang in blocks:
        text = wrap_between(text, before, after, lang)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    fix_gnn(ROOT / "posts/gnn_basics/index.qmd")
    fix_mongodb(ROOT / "posts/how-to-use-one-mongodb-instance-in-multiple-fastapi-routers/index.qmd")
    fix_bert(ROOT / "posts/bert/index.qmd")
    fix_solid(ROOT / "posts/solid-principles-with-python/index.qmd")
    fix_docker(ROOT / "posts/docker-get-started/index.qmd")
    print("Fixed code blocks in 5 posts.")


if __name__ == "__main__":
    main()
