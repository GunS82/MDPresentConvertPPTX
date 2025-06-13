from pathlib import Path

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from md2pptx.builder import build_presentation
from md2pptx.models import SlideModel, TextBlock


def test_build(tmp_path):
    slides = [SlideModel(title="Title", blocks=[TextBlock(text="Content")])]
    out = tmp_path / "out.pptx"
    build_presentation(slides, out)
    assert out.exists()
