from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from md2pptx.parser import parse_markdown


def test_parse_simple():
    slides = parse_markdown("# Title\n\nContent")
    assert len(slides) == 1
    assert slides[0].title == "Title"
