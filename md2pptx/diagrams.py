from __future__ import annotations

from pathlib import Path


def render(code: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / "diagram.png"
    # Stub: real implementation would invoke PlantUML
    output.write_bytes(b"")
    return output
