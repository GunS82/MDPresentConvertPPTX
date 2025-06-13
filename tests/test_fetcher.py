from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from md2pptx.fetcher import fetch_markdown


def test_fetch_local(tmp_path):
    md = tmp_path / "sample.md"
    md.write_text("# Title")
    text = fetch_markdown(str(md))
    assert "Title" in text
