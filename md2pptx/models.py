from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel

class ImageBlock(BaseModel):
    src: str
    alt: str = ""

class TextBlock(BaseModel):
    text: str
    bullets: Optional[List[str]] = None

class SlideModel(BaseModel):
    title: Optional[str]
    blocks: List[BaseModel]
    notes: Optional[str] = None
