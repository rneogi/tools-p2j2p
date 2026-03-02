from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def natural_key(path: Path) -> list[object]:
    import re

    parts = re.split(r"(\d+)", path.stem)
    key: list[object] = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part.lower())
    return key


def convert_jpgs_to_pdf(image_paths: list[Path], output_pdf: Path, dpi: int = 200) -> None:
    if not image_paths:
        raise ValueError("No JPG files found to combine.")

    rgb_images = []
    for path in image_paths:
        with Image.open(path) as img:
            rgb_images.append(img.convert("RGB"))

    first, rest = rgb_images[0], rgb_images[1:]
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    first.save(output_pdf, save_all=True, append_images=rest, resolution=float(dpi))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Combine sequential JPG files into a single PDF."
    )
    parser.add_argument(
        "input_glob",
        type=str,
        help='Glob pattern for JPG files (example: "abc*.jpg")',
    )
    parser.add_argument(
        "-o",
        "--output-pdf",
        required=True,
        type=Path,
        help="Path to output PDF file",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="Target PDF resolution metadata (default: 200)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    matches = [Path(p) for p in sorted(Path().glob(args.input_glob), key=natural_key)]
    if not matches:
        raise FileNotFoundError(f"No JPG files matched pattern: {args.input_glob}")

    convert_jpgs_to_pdf(matches, args.output_pdf, dpi=args.dpi)
    print(args.output_pdf)


if __name__ == "__main__":
    main()
