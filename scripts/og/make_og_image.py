"""Make the default link-preview image (1200 × 630) for WhatsApp and other apps.

Output: scripts/ingest/out/public/site/og-default.jpg (git-ignored; same layout as the R2 keys).
Upload: rclone copy --immutable scripts/ingest/out/public/site r2:f-section-media/public/site

Run: scripts\\ingest\\.venv\\Scripts\\python scripts\\og\\make_og_image.py
English only: Pillow on Windows has no complex-script shaping (raqm), so Tamil would render wrongly.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]
FONTS = REPO / "node_modules" / "@fontsource"
OUT = REPO / "scripts" / "ingest" / "out" / "public" / "site" / "og-default.jpg"

PAPER, INK, INK_RED, SEPIA, MARIGOLD, RULE = "#F6F1E7", "#1E2A3A", "#A23B2A", "#846541", "#E0A100", "#D9CDB6"
W, H = 1200, 630


def font(pkg: str, file: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / pkg / "files" / file), size)


def main() -> None:
    hand = lambda s: font("caveat", "caveat-latin-700-normal.woff", s)  # noqa: E731
    sans = lambda s: font("noto-sans-tamil", "noto-sans-tamil-latin-400-normal.woff", s)  # noqa: E731
    semi = lambda s: font("noto-sans-tamil", "noto-sans-tamil-latin-600-normal.woff", s)  # noqa: E731

    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)

    # Faint ruled lines, like an exercise-book page
    for y in range(150, H - 40, 48):
        d.line([(0, y), (W, y)], fill="#ECE3D2", width=2)
    d.line([(130, 0), (130, H)], fill="#E7B8AE", width=3)  # red margin line

    # Sepia "ink then" frame
    d.rectangle([24, 24, W - 25, H - 25], outline=SEPIA, width=6)

    x = 170
    d.text((x, 70), "1992 – 2026", font=hand(64), fill=SEPIA)
    d.text((x, 140), "F Section", font=hand(190), fill=INK)
    d.rectangle([x + 6, 365, x + 266, 373], fill=MARIGOLD)
    d.text((x, 400), "REC Trichy (NIT Trichy) · Class of 1996", font=semi(44), fill=INK)
    d.text((x, 465), "Photos, videos and the Arivu Malar magazine — 30 years on", font=sans(32), fill=INK_RED)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
