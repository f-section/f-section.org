"""Convert the Arivu Malar e-book pictures to WebP and stage them for R2.

Reads `out/photos.json` (written by extract.py) plus the two cover PNGs, writes a tree
under /mnt/data/f-section that mirrors the R2 keys exactly, and records each picture's
size in src/lib/ebook-img.json so the pages can reserve the right space before the
picture loads.

Nothing is uploaded here. Print the upload command with --upload-command, run it as a
dry run, and only then ask Saran (CLAUDE.md rule 3: `rclone copy`, never `sync`).

    scripts/ingest/.venv/bin/python scripts/arivumalar/media.py          # convert
    scripts/ingest/.venv/bin/python scripts/arivumalar/media.py --upload-command
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).resolve().parent / "out" / "photos.json"
SIZES = REPO / "src" / "lib" / "ebook-img.json"

WORK = Path("/mnt/data/f-section/arivumalar/2026")
EXPORT = WORK / "incoming" / "claude-design-arivumalar-source"
DESIGN = EXPORT / "design"
# Pictures Saran cropped out of the printed book himself, beside the export (2026-11-02).
CROPS = WORK / "incoming"
PDF_SRC = WORK / "incoming" / "Arivumalar-Full-book.pdf"
STAGE = WORK / "r2"  # STAGE/<r2 key> — so `rclone copy STAGE r2:bucket` lands right

PREFIX = "public/arivumalar/2026"
# One copy per picture, not a thumb/display pair: these sit in running text at about
# 34em, and the viewer only enlarges them to fit the screen. 1600px is enough for both
# and keeps the whole issue near 12 MB (rule 8).
MAX_EDGE = 1600
WEBP_QUALITY = 80

# The 1996 portraits are a case of their own (Saran, 2026-10-31). They are photographs
# of a printed halftone page, taken 30 years ago, and the design had scaled most of them
# up to 1200x1500 — at the width of a modern photograph they show nothing but their own
# dots. The page shows one at about 128px, so each becomes a single even thumbnail:
# trimmed of the odd scanned edge, pulled to the same tone and contrast as the rest,
# softened just enough to lose the print screen, and cut to the same 4:5 frame, so the
# nineteen read as one set rather than nineteen different photocopies.
THEN_SRC = "assets/family/old/"
CROP_SRC = "crops/"  # a 1996 portrait Saran cut out of the printed book
THEN_W, THEN_H = 320, 400  # twice what the page ever draws, for a sharp screen
THEN_MEAN, THEN_STD = 134.0, 58.0
THEN_ANCHOR = 0.35  # where the crop sits when a scan is too tall: heads are near the top
# A scan with the mount or the page edge still in it, as a fraction of each side.
THEN_TRIM = {
    "maragathavalli": (0.075, 0.045, 0.045, 0.015),
    "vairamuthu": (0.05, 0.04, 0.05, 0.03),  # the printed frame, rounded corners and all
    "sridhar": (0.05, 0.05, 0.05, 0.05),
}

# The two covers live at the root of the export, under their Tamil names.
COVERS = {
    f"{PREFIX}/cover-front.webp": "முன்_அட்டை.png",
    f"{PREFIX}/cover-back.webp": "பின்_அட்டை.png",
}


def convert(src: Path, dest: Path) -> tuple[int, int]:
    """One WebP copy, upright, never upscaled. Returns its size in pixels."""
    from PIL import Image, ImageOps

    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        im.thumbnail((MAX_EDGE, MAX_EDGE))
        dest.parent.mkdir(parents=True, exist_ok=True)
        # No EXIF: these are scans and design assets, and the gallery's reasons for
        # keeping it (date, GPS) do not apply here.
        im.save(dest, "WEBP", quality=WEBP_QUALITY, method=6)
        return im.size


def stretch(im):
    """
    Pull a scan's own range out to full black and white, reading the brightness only so
    that a colour photograph keeps its colour. (`autocontrast` does this per channel,
    which white-balances the colour away.)
    """
    hist = im.convert("L").histogram()
    total = sum(hist)
    lo, hi, run = 0, 255, 0
    for value, count in enumerate(hist):
        run += count
        if run >= total * 0.010:
            lo = value
            break
    run = 0
    for value in range(255, -1, -1):
        run += hist[value]
        if run >= total * 0.004:
            hi = value
            break
    if hi - lo < 32:  # a flat scan: leave it alone rather than amplify its noise
        return im
    table = [min(255, max(0, round((v - lo) * 255 / (hi - lo)))) for v in range(256)]
    return im.point(table * len(im.getbands()))


def even_tone(im):
    """The same brightness and contrast as the rest of the set, within reason."""
    from PIL import ImageEnhance, ImageStat

    im = stretch(im)
    stat = ImageStat.Stat(im.convert("L"))
    im = ImageEnhance.Contrast(im).enhance(min(1.25, max(0.85, THEN_STD / max(stat.stddev[0], 1))))
    stat = ImageStat.Stat(im.convert("L"))
    return ImageEnhance.Brightness(im).enhance(min(1.7, max(0.8, THEN_MEAN / max(stat.mean[0], 1))))


def crop_45(im):
    """The 4:5 frame every portrait shares. A tall scan loses the floor, not the face."""
    w, h = im.size
    if w / h > THEN_W / THEN_H:
        keep = round(h * THEN_W / THEN_H)
        left = (w - keep) // 2
        return im.crop((left, 0, left + keep, h))
    keep = round(w * THEN_H / THEN_W)
    top = round((h - keep) * THEN_ANCHOR)
    return im.crop((0, top, w, top + keep))


def portrait(src: Path, dest: Path) -> tuple[int, int]:
    """One 1996 portrait, as an even thumbnail. Returns its size in pixels."""
    from PIL import Image, ImageFilter

    with Image.open(src) as im:
        # The 1996 pages were printed in black and white, and a crop off the printed book
        # carries a photograph-of-a-page colour cast, so it is read as grey to match the
        # rest. The export's own scans are left in the mode they came in: they are already
        # grey in content, and re-encoding them would change objects that are live in R2.
        im = im.convert("L" if src.parent.name == "crops" or im.mode == "L" else "RGB")
        left, top, right, bottom = THEN_TRIM.get(src.stem, (0, 0, 0, 0))
        w, h = im.size
        im = im.crop((round(w * left), round(h * top), w - round(w * right), h - round(h * bottom)))
        im = even_tone(im)
        # Soften the print screen before the resize. A scan only a little larger than the
        # thumbnail needs more of this, not less: there is no downscale to average the
        # dots away, which is why the two photographs of photographs were the grainy ones.
        # A crop already smaller than the frame gets none, and nothing to sharpen either:
        # its dots are as soft as they go.
        shrink = im.height / THEN_H
        if shrink > 1.05:
            im = im.filter(ImageFilter.GaussianBlur(min(1.2, max(0.4, 1.7 / shrink))))
        im = crop_45(im)
        # Saran's own crops out of the printed book are small — 105 to 158px wide. Pulling
        # one up to 320px invents detail that is not there, so the frame stops at twice the
        # crop; the page draws it at 112–128px either way. A multiple of four keeps 4:5 exact.
        out_w = max(4, (min(THEN_W, 2 * im.width) // 4) * 4)
        out_h = out_w * THEN_H // THEN_W
        im = im.resize((out_w, out_h), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=70 if shrink > 1.05 else 40, threshold=3))
        dest.parent.mkdir(parents=True, exist_ok=True)
        im.save(dest, "WEBP", quality=82, method=6)
        return im.size


def human(n: int) -> str:
    return f"{n / 1024**2:.1f} MB" if n >= 1024**2 else f"{n / 1024:.0f} KB"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upload-command", action="store_true", help="print the rclone commands and stop")
    args = ap.parse_args(argv)

    if args.upload_command:
        print(f"# dry run first — nothing is written to R2:\n"
              f"rclone copy --immutable --dry-run -v {STAGE} r2:f-section-media\n\n"
              f"# then, only after Saran says yes:\n"
              f"rclone copy --immutable -v {STAGE} r2:f-section-media")
        return 0

    photos = json.loads(MANIFEST.read_text(encoding="utf-8"))
    # (r2 key, source file, how to convert it)
    jobs: list[tuple[str, Path, object]] = [
        (
            p["key"],
            (CROPS if p["source"].startswith(CROP_SRC) else DESIGN) / p["source"],
            portrait if p["source"].startswith((THEN_SRC, CROP_SRC)) else convert,
        )
        for p in photos
    ]
    jobs += [(key, EXPORT / name, convert) for key, name in COVERS.items()]

    sizes: dict[str, list[int]] = {}
    missing = [src for _, src, _ in jobs if not src.is_file()]
    if missing:
        for src in missing:
            print(f"missing source: {src}", file=sys.stderr)
        return 1

    for key, src, make in jobs:
        dest = STAGE / key
        w, h = make(src, dest)
        sizes[key] = [w, h]

    pdf = STAGE / PREFIX / "arivumalar-2026.pdf"
    pdf.parent.mkdir(parents=True, exist_ok=True)
    if not pdf.is_file() or pdf.stat().st_size != PDF_SRC.stat().st_size:
        shutil.copy2(PDF_SRC, pdf)

    SIZES.write_text(
        json.dumps(dict(sorted(sizes.items())), indent=0, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    pictures = sum((STAGE / k).stat().st_size for k in sizes)
    print(f"{len(sizes)} pictures  {human(pictures)}")
    print(f"the printable book  {human(pdf.stat().st_size)}")
    print(f"total               {human(pictures + pdf.stat().st_size)}")
    print(f"\nstaged in {STAGE}/{PREFIX}/")
    print(f"sizes written to {SIZES.relative_to(REPO)}")
    print("\nnext: --upload-command, run the dry run, then ask Saran before uploading")
    return 0


if __name__ == "__main__":
    sys.exit(main())
