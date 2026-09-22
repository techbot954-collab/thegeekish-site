#!/usr/bin/env python3
"""
Post Geekish stories to Facebook and Instagram through the Meta Graph API.

Required environment variables:
  META_ACCESS_TOKEN  Long-lived token with Page/Instagram publishing permissions.
  META_PAGE_ID       Facebook Page ID.
  META_IG_USER_ID    Instagram Business/Creator account ID.

Optional:
  GEEKISH_SITE_URL   Defaults to https://thegeekish.com
  META_AUTOPOST_STATE Defaults to .meta-autopost-state.json

Run with --dry-run to preview the next post without publishing.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_URL = os.environ.get("GEEKISH_SITE_URL", "https://thegeekish.com").rstrip("/")
STATE_PATH = Path(os.environ.get("META_AUTOPOST_STATE", ROOT / ".meta-autopost-state.json"))
GRAPH_BASE = "https://graph.facebook.com/v21.0"


class StoryParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stories: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if not href:
            return
        match = re.fullmatch(r"articles/([a-z0-9-]+)\.html", href)
        if match and match.group(1) not in self.stories:
            self.stories.append(match.group(1))


def extract_section(markdown: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)"
    match = re.search(pattern, markdown, flags=re.M | re.S)
    if not match:
        raise ValueError(f"Missing section: {heading}")
    return match.group("body").strip()


def extract_field(markdown: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}:\s*(.+)$", markdown, flags=re.M)
    if not match:
        raise ValueError(f"Missing field: {field}")
    return match.group(1).strip()


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"posted": []}
    with STATE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def newest_story_slugs() -> list[str]:
    parser = StoryParser()
    parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
    return parser.stories


def next_post() -> dict | None:
    state = load_state()
    posted = set(state.get("posted", []))
    for slug in newest_story_slugs():
        if slug in posted:
            continue
        post_path = ROOT / "social-posts" / f"{slug}.md"
        if not post_path.exists():
            continue
        markdown = post_path.read_text(encoding="utf-8")
        return {
            "slug": slug,
            "article_url": extract_field(markdown, "Article direct link"),
            "image_url": extract_field(markdown, "Image to post"),
            "facebook_caption": extract_section(markdown, "Facebook post"),
            "instagram_caption": extract_section(markdown, "Instagram feed caption"),
        }
    return None


def graph_post(path: str, params: dict[str, str]) -> dict:
    params["access_token"] = os.environ["META_ACCESS_TOKEN"]
    data = urllib.parse.urlencode(params).encode("utf-8")
    request = urllib.request.Request(f"{GRAPH_BASE}/{path.lstrip('/')}", data=data, method="POST")
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def publish(post: dict) -> dict:
    page_id = os.environ["META_PAGE_ID"]
    ig_user_id = os.environ["META_IG_USER_ID"]

    facebook = graph_post(
        f"{page_id}/photos",
        {
            "url": post["image_url"],
            "caption": post["facebook_caption"],
            "published": "true",
        },
    )

    instagram_container = graph_post(
        f"{ig_user_id}/media",
        {
            "image_url": post["image_url"],
            "caption": post["instagram_caption"],
        },
    )

    # Meta may need a moment to finish processing the image container.
    time.sleep(8)

    instagram = graph_post(
        f"{ig_user_id}/media_publish",
        {"creation_id": instagram_container["id"]},
    )

    return {"facebook": facebook, "instagram": instagram}


def mark_posted(slug: str, result: dict) -> None:
    state = load_state()
    state.setdefault("posted", [])
    if slug not in state["posted"]:
        state["posted"].append(slug)
    state.setdefault("history", []).append(
        {"slug": slug, "posted_at": int(time.time()), "result": result}
    )
    save_state(state)


def main() -> int:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--dry-run", action="store_true", help="Preview without publishing.")
    args = arg_parser.parse_args()

    post = next_post()
    if not post:
        print("No unposted Geekish stories found.")
        return 0

    print(json.dumps(post, indent=2))
    if args.dry_run:
        return 0

    missing = [
        name
        for name in ("META_ACCESS_TOKEN", "META_PAGE_ID", "META_IG_USER_ID")
        if not os.environ.get(name)
    ]
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        return 2

    result = publish(post)
    mark_posted(post["slug"], result)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
