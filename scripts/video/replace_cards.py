"""Replace the title cards in a montage with new ones, keeping every photo and the audio as they are.

Each new card (rendered by render-cards.mjs at 2x) is laid over the old card for exactly the same time
window, with a slow zoom and soft fades. While a card fades, a still frame from just outside the old card
is held beneath it, so the old card never shows through. Audio is copied without re-encoding.

Usage:
  python scripts/video/replace_cards.py --src "<montage.mov>" --out "<new.mp4>" \
      [--config scripts/video/montage-2026-30th.json] [--preview]

--preview renders only a few seconds around each card (fast), for checking.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CARDS = HERE / "out" / "cards@2x"


def ff(*args: str) -> None:
    exe = shutil.which("ffmpeg") or sys.exit("✗ ffmpeg not found (winget install Gyan.FFmpeg)")
    subprocess.run([exe, "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def still(src: Path, t: float, dest: Path) -> Path:
    ff("-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1", str(dest))
    return dest


def duration(path: Path, stream: str | None = None) -> float:
    """Container duration, or one stream's duration (e.g. stream='a:0')."""
    exe = shutil.which("ffprobe") or sys.exit("✗ ffprobe not found")
    what = ["-select_streams", stream, "-show_entries", "stream=duration"] if stream else ["-show_entries", "format=duration"]
    out = subprocess.run([exe, "-v", "error", *what, "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip().splitlines()[0])


def build(src: Path, out: Path, cfg: dict, window: tuple[float, float] | None, song: Path | None = None) -> None:
    fps = cfg["fps"]
    tmp = Path(tempfile.mkdtemp(prefix="cards-"))
    inputs: list[str] = ["-i", str(src)]
    chains: list[str] = []
    layers: list[tuple[str, str]] = []  # (label, kind) in overlay order: underlays first, then cards
    idx = 1
    cards = list(cfg["cards"])

    # Optional end card after the montage, with the song continued under it (cfg["ending"] + --song).
    # The montage audio is the song from 0 s, so the song picks up exactly where the montage stops.
    end = cfg.get("ending") if song else None
    src_len = duration(src)
    total = end["until"] if end else src_len
    if end:
        cards.append({"image": end["image"], "start": src_len - end["xfade"], "end": total,
                      "fade_in": end["xfade"], "fade_out": 0.0})

    def add_still(png: Path, start: float, dur: float, label: str) -> None:
        nonlocal idx
        inputs.extend(["-loop", "1", "-framerate", str(fps), "-t", f"{dur:.3f}", "-i", str(png)])
        chains.append(f"[{idx}:v]format=rgba,setpts=PTS-STARTPTS+{start:.3f}/TB[{label}]")
        idx += 1

    for n, c in enumerate(cards):
        if c.get("under_in") is not None and c["fade_in"] > 0:
            add_still(still(src, c["under_in"], tmp / f"u{n}in.png"), c["start"], c["fade_in"], f"u{n}i")
            layers.append((f"u{n}i", "under"))
        if c.get("under_out") is not None and c["fade_out"] > 0:
            add_still(still(src, c["under_out"], tmp / f"u{n}out.png"), c["end"] - c["fade_out"], c["fade_out"], f"u{n}o")
            layers.append((f"u{n}o", "under"))

    for n, c in enumerate(cards):
        dur = c["end"] - c["start"]
        frames = round(dur * fps)
        inputs.extend(["-loop", "1", "-framerate", str(fps), "-t", f"{dur:.3f}", "-i", str(CARDS / c["image"])])
        z = cfg["zoom"]
        fades = []
        if c["fade_in"] > 0:
            fades.append(f"fade=t=in:st=0:d={c['fade_in']}:alpha=1")
        if c["fade_out"] > 0:
            fades.append(f"fade=t=out:st={dur - c['fade_out']:.3f}:d={c['fade_out']}:alpha=1")
        chains.append(
            f"[{idx}:v]zoompan=z='1+{z}*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d=1:s=1920x1080:fps={fps},format=rgba,{','.join(fades)},"
            f"setpts=PTS-STARTPTS+{c['start']:.3f}/TB[c{n}]"
        )
        layers.append((f"c{n}", "card"))
        idx += 1

    prev = "0:v"
    if end:
        # Hold the last frame so the end card has something to fade in over and the video runs to `until`.
        chains.append(f"[0:v]tpad=stop_mode=clone:stop_duration={total - src_len:.3f}[base]")
        prev = "base"
    for i, (label, _) in enumerate(layers):
        nxt = f"v{i}"
        chains.append(f"[{prev}][{label}]overlay=eof_action=pass:format=auto[{nxt}]")
        prev = nxt
    finish = f",fade=t=out:st={total - end['fade_out']:.3f}:d={end['fade_out']}" if end else ""
    chains.append(f"[{prev}]fade=t=in:st=0:d={cfg['fade_from_black']}{finish},format=yuv420p[vout]")

    if end:
        # Montage audio up to its end, then the same song from that exact second (tiny crossfade to
        # avoid a click), fading out with the picture on a pause in the music.
        xf = end["audio_xfade"]
        a_len = duration(src, "a:0")  # join at the audio's own end, which can differ from the video's by ms
        inputs.extend(["-i", str(song)])
        chains.append(f"[0:a:0]aresample=44100,aformat=channel_layouts=stereo[a0]")
        chains.append(f"[{idx}:a:0]atrim=start={a_len - xf:.4f}:end={total:.4f},asetpts=PTS-STARTPTS,"
                      f"aresample=44100,aformat=channel_layouts=stereo[a1]")
        chains.append(f"[a0][a1]acrossfade=d={xf}:c1=tri:c2=tri,"
                      f"afade=t=out:st={total - end['fade_out']:.3f}:d={end['fade_out']}[aout]")
        amap, acodec = ["-map", "[aout]"], ["-c:a", "aac", "-b:a", "256k"]
    else:
        amap, acodec = ["-map", "0:a:0"], ["-c:a", "copy"]

    trim: list[str] = []
    if window:
        trim = ["-ss", f"{window[0]:.3f}", "-to", f"{window[1]:.3f}"]

    ff(*inputs, "-filter_complex", ";".join(chains), "-map", "[vout]", *amap,
       *trim, "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-r", str(fps),
       *acodec, "-movflags", "+faststart", str(out))
    shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--config", type=Path, default=HERE / "montage-2026-30th.json")
    ap.add_argument("--song", type=Path, help="the montage's song, to continue it under the end card (cfg['ending'])")
    ap.add_argument("--preview", action="store_true", help="render short clips around each card only")
    a = ap.parse_args()
    cfg = json.loads(a.config.read_text("utf-8"))
    if a.out.resolve() == a.src.resolve():
        sys.exit("✗ --out must differ from --src; the original is never overwritten.")
    if not a.preview:
        build(a.src, a.out, cfg, None, a.song)
        print(f"✓ {a.out}")
        return
    for n, c in enumerate(cfg["cards"]):
        clip = a.out.with_name(f"{a.out.stem}-preview-{n + 1}.mp4")
        build(a.src, clip, cfg, (max(0.0, c["start"] - 2.0), c["end"] + 2.0), a.song)
        print(f"✓ {clip}")


if __name__ == "__main__":
    main()
