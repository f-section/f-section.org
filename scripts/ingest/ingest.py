"""Ingest one album of originals into web copies, media.json and R2 (DESIGN.md §8).

Dry run is the default: it only prints the plan. Pass --apply to write files.

Rules (CLAUDE.md):
  * Photos are already curated by Saran, so location is KEPT: the display copy keeps
    its EXIF (date and GPS) and media.json records the coordinates for a map link.
    Thumbnails carry no metadata, to stay small.
  * Uploads use `rclone copy --immutable`: never `sync`, never overwrite.
  * Originals are only read, never changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ALBUMS_DIR = REPO / "src" / "content" / "albums"
OUT_DIR = Path(__file__).resolve().parent / "out"

PHOTO_EXT = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".heic", ".heif"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".avi", ".mts", ".3gp", ".mkv"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}

THUMB_EDGE = 480
DISPLAY_EDGE = 2048
WEBP_QUALITY = 80
BUDGET_WARN_BYTES = 8 * 1024**3  # warn at 8 GB (free tier is 10 GB)

EXIF_DATETIME_ORIGINAL = 0x9003
EXIF_DATETIME = 0x0132
EXIF_IFD = 0x8769
GPS_IFD = 0x8825

SLUG = re.compile(r"^\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*$")


# --------------------------------------------------------------------------- helpers


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "unknown"


def rel(path: Path) -> str:
    """Path relative to the repo for messages, or absolute if outside it."""
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024
    return f"{n:.1f} GB"


def need_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        sys.exit(
            f"✗ `{name}` is not installed or not on PATH.\n"
            f"  On Windows: winget install {'Rclone.Rclone' if name == 'rclone' else 'Gyan.FFmpeg'}"
        )
    return path


def read_visibility(album_dir: Path) -> str:
    album_yaml = album_dir / "album.yaml"
    if not album_yaml.exists():
        sys.exit(f"✗ {rel(album_yaml)} not found. Create album.yaml first (DESIGN.md §10.1).")
    m = re.search(r"^visibility:\s*(public|members)\s*(#.*)?$", album_yaml.read_text("utf-8"), re.M)
    if not m:
        sys.exit(f"✗ {rel(album_yaml)} has no valid `visibility:` (public or members).")
    return m.group(1)


def load_manifest(album_dir: Path) -> list[dict]:
    p = album_dir / "media.json"
    if not p.exists():
        return []
    return json.loads(p.read_text("utf-8"))


def write_manifest(album_dir: Path, items: list[dict]) -> None:
    items = sorted(items, key=lambda m: m["id"])
    text = json.dumps(items, indent=2, ensure_ascii=False) + "\n"
    (album_dir / "media.json").write_bytes(text.encode("utf-8"))


# --------------------------------------------------------------------------- planning


@dataclass
class Planned:
    src: Path
    kind: str  # photo | video | audio
    contributor: str
    taken: datetime | None
    taken_source: str  # exif | ffprobe | mtime | scan
    sha256: str
    id: str = ""
    duplicate_of: str | None = None
    notes: list[str] = field(default_factory=list)


def kind_of(path: Path) -> str | None:
    ext = path.suffix.lower()
    if ext in PHOTO_EXT:
        return "photo"
    if ext in VIDEO_EXT:
        return "video"
    if ext in AUDIO_EXT:
        return "audio"
    return None


def open_image(path: Path):
    from PIL import Image

    if path.suffix.lower() in {".heic", ".heif"}:
        try:
            import pillow_heif  # type: ignore

            pillow_heif.register_heif_opener()
        except ImportError:
            raise RuntimeError("HEIC needs `pip install pillow-heif`")
    return Image.open(path)


def photo_taken(path: Path) -> datetime | None:
    try:
        with open_image(path) as im:
            exif = im.getexif()
            raw = exif.get_ifd(EXIF_IFD).get(EXIF_DATETIME_ORIGINAL) or exif.get(EXIF_DATETIME)
    except Exception:
        return None
    if not raw:
        return None
    try:
        return datetime.strptime(str(raw).strip("\x00 ")[:19], "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None


def media_taken(path: Path) -> datetime | None:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    try:
        out = subprocess.run(
            [ffprobe, "-v", "quiet", "-print_format", "json", "-show_entries", "format_tags=creation_time", str(path)],
            capture_output=True, text=True, check=True,
        ).stdout
        ct = json.loads(out).get("format", {}).get("tags", {}).get("creation_time")
        if ct:
            return datetime.fromisoformat(ct.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None
    return None


def contributor_for(path: Path, src_root: Path, default: str | None) -> str:
    if default:
        return slugify(default)
    parts = path.relative_to(src_root).parts
    if len(parts) > 1:
        return slugify(parts[0])
    return "unknown"


def plan(src_root: Path, existing: list[dict], contributor: str | None, scan_year: int | None) -> list[Planned]:
    known = {m.get("sha256"): m["id"] for m in existing if m.get("sha256")}
    # Continue numbering per contributor after the highest existing number.
    counters: dict[str, int] = {}
    for m in existing:
        parts = m["id"].split("_")
        if len(parts) == 3 and parts[2].isdigit():
            counters[parts[1]] = max(counters.get(parts[1], 0), int(parts[2]))

    files = sorted(p for p in src_root.rglob("*") if p.is_file())
    planned: list[Planned] = []
    seen: dict[str, str] = {}
    for f in files:
        kind = kind_of(f)
        if not kind:
            continue
        digest = sha256_of(f)
        who = "scan" if scan_year else contributor_for(f, src_root, contributor)
        if scan_year:
            taken, source = None, "scan"
        else:
            taken = photo_taken(f) if kind == "photo" else media_taken(f)
            source = "exif" if kind == "photo" else "ffprobe"
            if taken is None:
                taken, source = datetime.fromtimestamp(f.stat().st_mtime), "mtime"
        item = Planned(src=f, kind=kind, contributor=who, taken=taken, taken_source=source, sha256=digest)
        if digest in known:
            item.duplicate_of = known[digest]
        elif digest in seen:
            item.duplicate_of = seen[digest]
        if source == "mtime":
            item.notes.append("no date in file; used file modified time")
        planned.append(item)
        if not item.duplicate_of:
            seen[digest] = "(this run)"

    # Assign ids in time order so numbers follow the order photos were taken.
    fresh = [p for p in planned if not p.duplicate_of]
    fresh.sort(key=lambda p: (p.taken or datetime.min, p.src.name))
    for p in fresh:
        counters[p.contributor] = counters.get(p.contributor, 0) + 1
        n = counters[p.contributor]
        if scan_year:
            p.id = f"{scan_year:04d}-00-00_scan_{n:03d}"
        else:
            p.id = f"{p.taken:%Y%m%d-%H%M%S}_{p.contributor}_{n:03d}"
        seen[p.sha256] = p.id
    for p in planned:
        if p.duplicate_of == "(this run)":
            p.duplicate_of = seen[p.sha256]
    return planned


# --------------------------------------------------------------------------- processing


def has_gps(path: Path) -> bool:
    from PIL import Image

    with Image.open(path) as im:
        exif = im.getexif()
        return GPS_IFD in exif or bool(exif.get_ifd(GPS_IFD))


def _dms_to_deg(dms, ref) -> float | None:
    try:
        d, m, s = (float(x) for x in dms)
    except (TypeError, ValueError):
        return None
    deg = d + m / 60 + s / 3600
    return -deg if str(ref).strip("\x00 ").upper() in ("S", "W") else deg


def photo_gps(path: Path) -> dict | None:
    """{lat, lon} from a photo's EXIF, or None."""
    try:
        with open_image(path) as im:
            g = im.getexif().get_ifd(GPS_IFD)
    except Exception:
        return None
    if not g or 2 not in g or 4 not in g:
        return None
    lat, lon = _dms_to_deg(g[2], g.get(1, "N")), _dms_to_deg(g[4], g.get(3, "E"))
    if lat is None or lon is None or (lat == 0 and lon == 0):
        return None
    return {"lat": round(lat, 6), "lon": round(lon, 6)}


def video_gps(path: Path) -> dict | None:
    """{lat, lon} from a phone video's ISO 6709 `location` tag, or None."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    try:
        out = subprocess.run(
            [ffprobe, "-v", "quiet", "-print_format", "json", "-show_entries", "format_tags", str(path)],
            capture_output=True, text=True, check=True,
        ).stdout
        tags = {k.lower(): v for k, v in json.loads(out).get("format", {}).get("tags", {}).items()}
    except Exception:
        return None
    loc = tags.get("location") or tags.get("com.apple.quicktime.location.iso6709")
    m = re.match(r"^([+-]\d+(?:\.\d+)?)([+-]\d+(?:\.\d+)?)", loc or "")
    return {"lat": round(float(m.group(1)), 6), "lon": round(float(m.group(2)), 6)} if m else None


def process_photo(p: Planned, out: Path) -> dict:
    """Write thumb and display WebP copies. Returns manifest fields.

    The display copy keeps the EXIF (date taken, GPS, camera) with orientation reset,
    because it has been rotated upright. The thumbnail carries no metadata, to stay small.
    """
    from PIL import ImageOps

    with open_image(p.src) as im:
        im = ImageOps.exif_transpose(im)  # rotate the right way up; orientation tag is reset
        exif_bytes = im.getexif().tobytes()
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        results = {}
        for size, edge in (("thumb", THUMB_EDGE), ("display", DISPLAY_EDGE)):
            copy = im.copy()
            copy.thumbnail((edge, edge))  # keeps aspect ratio, never upscales
            dest = out / size / f"{p.id}.webp"
            dest.parent.mkdir(parents=True, exist_ok=True)
            extra = {"exif": exif_bytes} if size == "display" and exif_bytes else {}
            copy.save(dest, "WEBP", quality=WEBP_QUALITY, method=6, **extra)
            results[size] = copy.size
    w, h = results["display"]
    fields: dict = {"width": w, "height": h}
    gps = photo_gps(p.src)
    if gps:
        fields["gps"] = gps
    return fields


def run_ffmpeg(args: list[str]) -> None:
    ffmpeg = need_tool("ffmpeg")
    subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def probe_size(path: Path) -> tuple[int, int]:
    ffprobe = need_tool("ffprobe")
    out = subprocess.run(
        [ffprobe, "-v", "quiet", "-print_format", "json", "-select_streams", "v:0", "-show_entries", "stream=width,height", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    s = json.loads(out)["streams"][0]
    return int(s["width"]), int(s["height"])


def process_video(p: Planned, out: Path) -> dict:
    dest = out / "video"
    dest.mkdir(parents=True, exist_ok=True)
    for height, rate, maxrate in (("1080", "5M", "5.5M"), ("720", "2.5M", "2.8M")):
        run_ffmpeg([
            "-i", str(p.src), "-map", "0:v:0", "-map", "0:a:0?",
            "-vf", f"scale=-2:'min({height},ih)'",
            "-c:v", "libx264", "-preset", "slow", "-b:v", rate, "-maxrate", maxrate, "-bufsize", "10M",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            str(dest / f"{p.id}-{height}.mp4"),
        ])
    run_ffmpeg(["-ss", "1", "-i", str(p.src), "-frames:v", "1", "-vf", "scale=-2:'min(720,ih)'", "-q:v", "3", str(dest / f"{p.id}.jpg")])
    w, h = probe_size(dest / f"{p.id}-1080.mp4")
    fields: dict = {"width": w, "height": h}
    gps = video_gps(p.src)
    if gps:
        fields["gps"] = gps
    return fields


def process_audio(p: Planned, out: Path) -> dict:
    dest = out / "audio"
    dest.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(["-i", str(p.src), "-vn", "-c:a", "libmp3lame", "-b:a", "128k", str(dest / f"{p.id}.mp3")])
    return {}


# --------------------------------------------------------------------------- upload


def upload(local: Path, remote: str, bucket: str, key_prefix: str) -> None:
    rclone = need_tool("rclone")
    target = f"{remote}:{bucket}/{key_prefix}"
    print(f"\n↑ rclone copy --immutable {local} {target}")
    # --immutable: fail rather than modify any object that already exists.
    subprocess.run([rclone, "copy", "--immutable", "--progress", str(local), target], check=True)
    out = subprocess.run([rclone, "size", "--json", f"{remote}:{bucket}"], capture_output=True, text=True, check=True).stdout
    total = json.loads(out).get("bytes", 0)
    print(f"\nBucket {bucket}: {human(total)} used of the 10 GB free tier.")
    if total >= BUDGET_WARN_BYTES:
        print("⚠ WARNING: R2 storage is at or above 8 GB. Tell Saran before uploading more (DESIGN.md §9).")


# --------------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python scripts/ingest",
        description="Turn one album of originals into web copies, update media.json and upload to R2. "
        "Dry run by default.",
    )
    ap.add_argument("--album", required=True, help="album slug, e.g. 2026-reunion-campus-walk")
    ap.add_argument("--src", required=True, type=Path, help="folder of chosen originals (e.g. on the NAS)")
    ap.add_argument("--contributor", help="name for all files; default is each file's first subfolder name")
    ap.add_argument("--scan-year", type=int, help="old scanned photos with no exact date: name them YYYY-00-00_scan_NNN")
    ap.add_argument("--apply", action="store_true", help="actually process, write media.json and upload")
    ap.add_argument("--no-upload", action="store_true", help="with --apply: process and write media.json, skip upload")
    ap.add_argument("--remote", default=os.environ.get("FSECTION_RCLONE_REMOTE", "r2"), help="rclone remote name (default r2)")
    ap.add_argument("--bucket", default="f-section-media")
    args = ap.parse_args(argv)

    if not SLUG.match(args.album):
        sys.exit("✗ Album slug must look like YYYY-event-topic (lowercase, hyphens).")
    if not args.src.is_dir():
        sys.exit(f"✗ Source folder not found: {args.src}")

    album_dir = ALBUMS_DIR / args.album
    visibility = read_visibility(album_dir)
    existing = load_manifest(album_dir)
    planned = plan(args.src, existing, args.contributor, args.scan_year)
    fresh = [p for p in planned if not p.duplicate_of]
    dupes = [p for p in planned if p.duplicate_of]

    print(f"Album {args.album} ({visibility}), source {args.src}")
    print(f"{len(planned)} media files: {len(fresh)} new, {len(dupes)} already in the album or repeated\n")
    for p in planned:
        if p.duplicate_of:
            print(f"  = {p.src.name}  →  skip, same file as {p.duplicate_of}")
        else:
            note = f"  ({'; '.join(p.notes)})" if p.notes else ""
            print(f"  + {p.src.name}  →  {p.id}  [{p.kind}]{note}")

    key_prefix = f"{visibility}/albums/{args.album}"
    out = OUT_DIR / key_prefix

    if not args.apply:
        print(f"\nDry run: nothing written. Web copies would go to {out}")
        print(f"and be uploaded to {args.remote}:{args.bucket}/{key_prefix}/ with rclone copy --immutable.")
        print("Run again with --apply to do it.")
        return 0

    if not fresh:
        print("\nNothing new to add.")
        return 0

    new_items = []
    for p in fresh:
        print(f"  … {p.id}")
        if p.kind == "photo":
            dims = process_photo(p, out)
        elif p.kind == "video":
            dims = process_video(p, out)
        else:
            dims = process_audio(p, out)
        new_items.append({
            "id": p.id,
            "type": p.kind,
            **dims,
            "sha256": p.sha256,
            "credit": "" if p.contributor in ("scan", "unknown") else p.contributor,
            "taken": str(args.scan_year) if args.scan_year else p.taken.isoformat(timespec="seconds"),
            "caption": {"en": "", "ta": ""},
        })

    write_manifest(album_dir, existing + new_items)
    print(f"\n✓ Wrote {len(new_items)} new items to {rel(album_dir / 'media.json')}")

    if args.no_upload:
        print(f"Skipped upload (--no-upload). Web copies are in {out}")
        return 0
    upload(out, args.remote, args.bucket, key_prefix)
    print("\nNext: commit media.json to the staging branch and check the preview on a phone.")
    return 0
