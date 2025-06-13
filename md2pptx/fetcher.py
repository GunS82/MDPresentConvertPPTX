from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

GIST_RE = re.compile(r"^[0-9a-f]{20,}$")

def fetch_markdown(src: str) -> str:
    if src.startswith("http://") or src.startswith("https://"):
        return _fetch_from_url(src)
    elif GIST_RE.match(src):
        return _fetch_from_gist(src)
    else:
        path = Path(src)
        return path.read_text(encoding="utf-8")

def _fetch_from_url(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def _fetch_from_gist(gist_id: str) -> str:
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    api_url = f"https://api.github.com/gists/{gist_id}"
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    gist = response.json()
    for file_info in gist["files"].values():
        if file_info["filename"].endswith(".md"):
            raw_url = file_info["raw_url"]
            return _fetch_from_url(raw_url)
    raise ValueError("No markdown file found in gist")
