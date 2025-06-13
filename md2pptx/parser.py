from __future__ import annotations

import re
from typing import List

from bs4 import BeautifulSoup
import markdown

from .models import SlideModel, TextBlock, ImageBlock

SEPARATOR = re.compile(r"^---$", re.MULTILINE)


def parse_markdown(text: str) -> List[SlideModel]:
    parts = [p.strip() for p in SEPARATOR.split(text) if p.strip()]
    slides: List[SlideModel] = []
    for part in parts:
        html = markdown.markdown(part)
        soup = BeautifulSoup(html, "html.parser")
        title_el = soup.find(["h1", "h2", "strong"])
        title = title_el.get_text(strip=True) if title_el else None
        blocks = []
        bullets = [li.get_text(strip=True) for li in soup.find_all("li")]
        if bullets:
            blocks.append(TextBlock(text="", bullets=bullets))
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        for p in paragraphs:
            if p:
                blocks.append(TextBlock(text=p))
        for img in soup.find_all("img"):
            blocks.append(ImageBlock(src=img["src"], alt=img.get("alt", "")))
        slides.append(SlideModel(title=title, blocks=blocks))
    return slides
