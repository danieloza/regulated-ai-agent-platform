from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def build_demo(frame_dir: Path, output: Path, duration_ms: int) -> None:
    paths = sorted(frame_dir.glob("*.png"))
    if not paths:
        raise SystemExit(f"No PNG frames found in {frame_dir}")

    frames: list[Image.Image] = []
    expected_size: tuple[int, int] | None = None
    for path in paths:
        with Image.open(path) as source:
            frame = source.convert("RGB")
            if expected_size is None:
                expected_size = frame.size
            if frame.size != expected_size:
                raise SystemExit(f"Frame {path.name} has size {frame.size}; expected {expected_size}.")
            frames.append(frame.quantize(colors=96, method=Image.Quantize.MEDIANCUT))

    output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
        optimize=True,
    )
    print(f"Wrote {len(frames)} frames at {expected_size[0]}x{expected_size[1]} to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the high-resolution README demo from ordered PNG frames.")
    parser.add_argument("frame_dir", type=Path)
    parser.add_argument("--output", type=Path, default=Path("docs/demo.gif"))
    parser.add_argument("--duration-ms", type=int, default=2200)
    args = parser.parse_args()
    build_demo(args.frame_dir.resolve(), args.output.resolve(), args.duration_ms)


if __name__ == "__main__":
    main()
