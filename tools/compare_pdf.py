from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean

try:
    import pymupdf as fitz
except ImportError:  # pragma: no cover
    import fitz
from PIL import Image, ImageChops, ImageStat


@dataclass
class PageDiff:
    page: int
    same_size: bool
    rms_diff: float
    similar: bool


@dataclass
class CompareResult:
    page_count_a: int
    page_count_b: int
    same_page_count: bool
    threshold_rms: float
    page_results: list[PageDiff]

    @property
    def equivalent(self) -> bool:
        return self.same_page_count and all(p.similar for p in self.page_results)

    @property
    def avg_rms_diff(self) -> float:
        if not self.page_results:
            return 0.0
        return mean(p.rms_diff for p in self.page_results)


def render_page(page: fitz.Page, dpi: int = 200) -> Image.Image:
    zoom = dpi / 72.0
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def _rms_diff(img_a: Image.Image, img_b: Image.Image) -> float:
    diff = ImageChops.difference(img_a, img_b)
    stat = ImageStat.Stat(diff)
    channel_rms = stat.rms
    return float(sum(channel_rms) / len(channel_rms))


def compare_pdfs(pdf_a: Path, pdf_b: Path, dpi: int = 200, threshold_rms: float = 10.0) -> CompareResult:
    with fitz.open(pdf_a) as doc_a, fitz.open(pdf_b) as doc_b:
        same_page_count = len(doc_a) == len(doc_b)
        page_results: list[PageDiff] = []

        for page_number in range(1, min(len(doc_a), len(doc_b)) + 1):
            img_a = render_page(doc_a[page_number - 1], dpi=dpi)
            img_b = render_page(doc_b[page_number - 1], dpi=dpi)
            same_size = img_a.size == img_b.size
            if not same_size:
                img_b = img_b.resize(img_a.size, Image.Resampling.LANCZOS)

            rms = _rms_diff(img_a, img_b)
            similar = rms <= threshold_rms

            page_results.append(
                PageDiff(
                    page=page_number,
                    same_size=same_size,
                    rms_diff=rms,
                    similar=similar,
                )
            )

        return CompareResult(
            page_count_a=len(doc_a),
            page_count_b=len(doc_b),
            same_page_count=same_page_count,
            threshold_rms=threshold_rms,
            page_results=page_results,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare two PDFs by rendering each page and checking pixel equality."
    )
    parser.add_argument("pdf_a", type=Path)
    parser.add_argument("pdf_b", type=Path)
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--threshold-rms", type=float, default=10.0)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    result = compare_pdfs(
        args.pdf_a,
        args.pdf_b,
        dpi=args.dpi,
        threshold_rms=args.threshold_rms,
    )
    payload = {
        **asdict(result),
        "avg_rms_diff": result.avg_rms_diff,
        "equivalent": result.equivalent,
    }

    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Equivalent: {result.equivalent}")
        print(f"Page counts: {result.page_count_a} vs {result.page_count_b}")
        print(f"Average RMS diff: {result.avg_rms_diff:.4f} (threshold={result.threshold_rms})")
        for pr in result.page_results:
            print(
                f"Page {pr.page}: same_size={pr.same_size}, rms_diff={pr.rms_diff:.4f}, similar={pr.similar}"
            )


if __name__ == "__main__":
    main()
