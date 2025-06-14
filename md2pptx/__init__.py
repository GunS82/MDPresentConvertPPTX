"""MDPresentConvertPPTX - Simple converter from Markdown to PowerPoint slides."""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .parser import parse_markdown
from .builder import build_presentation
from .fetcher import fetch_markdown
from .models import SlideModel, TextBlock, ImageBlock

__all__ = [
    "parse_markdown",
    "build_presentation", 
    "fetch_markdown",
    "SlideModel",
    "TextBlock",
    "ImageBlock",
]