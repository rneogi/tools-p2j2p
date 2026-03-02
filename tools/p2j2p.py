from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from compare_pdf import compare_pdfs
from jpg2pdf import convert_jpgs_to_pdf, natural_key
from pdf2jpg import convert_pdf_to_jpg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Roundtrip PDF -> JPG pages -> PDF and verify similarity."
    )
    parser.add_argument("input_pdf", type=Path, help="Input PDF path")
    parser.add_argument("--dpi", type=int, default=200, help="Render DPI (default: 200)")
    parser.add_argument(
        "--threshold-rms",
        type=float,
        default=10.0,
        help="Similarity threshold for page RMS diff (default: 10)",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep intermediate JPG files in .claude/tmp/p2j2p",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    input_pdf = args.input_pdf

    if not input_pdf.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_pdf}")

    stem = input_pdf.stem
    work_dir = Path(".claude") / "tmp" / "p2j2p" / stem
    output_pdf = input_pdf.parent / f"{stem}-new.pdf"

    try:
        convert_pdf_to_jpg(
            input_pdf=input_pdf,
            output_dir=work_dir,
            output_prefix=stem,
            dpi=args.dpi,
        )

        jpgs = sorted(work_dir.glob(f"{stem}*.jpg"), key=natural_key)
        convert_jpgs_to_pdf(jpgs, output_pdf=output_pdf, dpi=args.dpi)

        result = compare_pdfs(
            input_pdf,
            output_pdf,
            dpi=args.dpi,
            threshold_rms=args.threshold_rms,
        )

        payload = {
            "input": str(input_pdf),
            "output": str(output_pdf),
            "page_count_a": result.page_count_a,
            "page_count_b": result.page_count_b,
            "same_page_count": result.same_page_count,
            "avg_rms_diff": result.avg_rms_diff,
            "threshold_rms": result.threshold_rms,
            "equivalent": result.equivalent,
            "differing_pages": [p.page for p in result.page_results if not p.similar],
        }

        if args.as_json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"Input: {payload['input']}")
            print(f"Output: {payload['output']}")
            print(
                f"Pages: {payload['page_count_a']} vs {payload['page_count_b']} (match={payload['same_page_count']})"
            )
            print(
                f"Equivalent: {payload['equivalent']} (avg_rms_diff={payload['avg_rms_diff']:.4f}, threshold={payload['threshold_rms']})"
            )
            if payload["differing_pages"]:
                print(f"Differing pages: {payload['differing_pages']}")
    finally:
        if args.keep_temp:
            print(f"Kept temp files: {work_dir}")
        elif work_dir.exists():
            shutil.rmtree(work_dir, ignore_errors=True)
            print(f"Cleaned temp files: {work_dir}")


if __name__ == "__main__":
    main()
