from __future__ import annotations

import argparse
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:  # pragma: no cover
    import fitz


def convert_pdf_to_jpg(
    input_pdf: Path,
    output_dir: Path,
    output_prefix: str,
    dpi: int = 200,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    created_files: list[Path] = []

    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    with fitz.open(input_pdf) as doc:
        for page_index, page in enumerate(doc, start=1):
            output_path = output_dir / f"{output_prefix}{page_index}.jpg"
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            pix.save(str(output_path), jpg_quality=95)
            created_files.append(output_path)

    return created_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert each page of a PDF into sequential JPG files."
    )
    parser.add_argument("input_pdf", type=Path, help="Path to the input PDF file")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for generated JPG files (default: same folder as input PDF)",
    )
    parser.add_argument(
        "-p",
        "--output-prefix",
        type=str,
        default=None,
        help="Prefix for generated files (default: PDF filename without extension)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="Render DPI for JPG output (default: 200)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    input_pdf: Path = args.input_pdf
    if not input_pdf.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_pdf}")

    output_dir = args.output_dir or input_pdf.parent
    output_prefix = args.output_prefix or input_pdf.stem

    files = convert_pdf_to_jpg(
        input_pdf=input_pdf,
        output_dir=output_dir,
        output_prefix=output_prefix,
        dpi=args.dpi,
    )

    for file_path in files:
        print(file_path)


if __name__ == "__main__":
    main()
