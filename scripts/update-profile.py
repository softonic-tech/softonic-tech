#!/usr/bin/env python3
"""Refresh the daily quote and last-updated timestamp in README.md."""

from __future__ import annotations

import json
import re
import urllib.request
from datetime import datetime, timezone

README = "README.md"
USER_AGENT = "softonic-tech-profile-bot"

FALLBACK_QUOTES = [
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("Simplicity is the soul of efficiency.", "Austin Freeman"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
    ("Make it work, make it right, make it fast.", "Kent Beck"),
]


def fetch_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_quote() -> tuple[str, str]:
    try:
        data = fetch_json("https://zenquotes.io/api/today")
        item = data[0]
        return item["q"].strip(), item["a"].strip()
    except Exception:
        pass

    try:
        data = fetch_json("https://api.quotable.io/random?tags=technology|wisdom")
        return data["content"].strip(), data["author"].strip()
    except Exception:
        day = datetime.now(timezone.utc).timetuple().tm_yday
        return FALLBACK_QUOTES[day % len(FALLBACK_QUOTES)]


def replace_section(content: str, name: str, inner: str) -> str:
    pattern = rf"(<!--START_SECTION:{name}-->)(.*?)(<!--END_SECTION:{name}-->)"
    replacement = rf"\1\n{inner}\n\3"
    updated, count = re.subn(pattern, replacement, content, flags=re.S)
    if count == 0:
        raise SystemExit(f"Missing README section markers for: {name}")
    return updated


def main() -> None:
    quote, author = fetch_quote()
    now = datetime.now(timezone.utc).strftime("%B %d, %Y · %H:%M UTC")
    quote_md = f"> “{quote}”\n>\n> — **{author}**"
    updated_md = f"📅 Last refreshed: **{now}**"

    with open(README, encoding="utf-8") as handle:
        content = handle.read()

    content = replace_section(content, "quote", quote_md)
    content = replace_section(content, "updated", updated_md)

    with open(README, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)

    print(f"Updated quote by {author}")
    print(f"Updated timestamp to {now}")


if __name__ == "__main__":
    main()
