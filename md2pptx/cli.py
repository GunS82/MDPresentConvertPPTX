import argparse
from pathlib import Path
from .fetcher import fetch_markdown
from .parser import parse_markdown
from .builder import build_presentation


def main() -> None:
    parser = argparse.ArgumentParser(description="Markdown to PPTX converter")
    parser.add_argument("source", help="Markdown file path, URL, or Gist ID")
    parser.add_argument("-o", "--output", default="slides.pptx", help="Output PPTX file")
    parser.add_argument("-t", "--template", default=None, help="PPTX template")

    args = parser.parse_args()

    md_text = fetch_markdown(args.source)
    slides = parse_markdown(md_text)
    build_presentation(slides, Path(args.output), template=args.template)


if __name__ == "__main__":
    main()
