"""Tests for the ingest script. Run: python -m unittest discover -s scripts/ingest/tests"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image  # noqa: E402

import ingest  # noqa: E402


def make_photo(path: Path, size=(3000, 2000), taken="2026:09:12 10:15:33", orientation=None, gps=True):
    """A JPEG with a date, optional EXIF orientation and fake GPS coordinates."""
    path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGB", size, (200, 120, 60))
    exif = im.getexif()
    exif.get_ifd(ingest.EXIF_IFD)[ingest.EXIF_DATETIME_ORIGINAL] = taken
    if orientation:
        exif[0x0112] = orientation
    if gps:
        g = exif.get_ifd(ingest.GPS_IFD)
        g[1] = "N"
        g[2] = (10.0, 45.0, 30.0)
        g[3] = "E"
        g[4] = (78.0, 49.0, 0.0)
    im.save(path, "JPEG", exif=exif)
    return path


class IngestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.albums = self.tmp / "albums"
        self.out = self.tmp / "out"
        self.src = self.tmp / "originals"
        self.album = self.albums / "2026-test-album"
        self.album.mkdir(parents=True)
        (self.album / "album.yaml").write_text("slug: 2026-test-album\nvisibility: public\n", "utf-8")
        self._saved = (ingest.ALBUMS_DIR, ingest.OUT_DIR)
        ingest.ALBUMS_DIR, ingest.OUT_DIR = self.albums, self.out

    def tearDown(self):
        ingest.ALBUMS_DIR, ingest.OUT_DIR = self._saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_fixture_really_has_gps(self):
        p = make_photo(self.src / "saran" / "a.jpg")
        self.assertTrue(ingest.has_gps(p))

    def test_photo_web_copies_have_no_gps_and_are_upright(self):
        p = make_photo(self.src / "saran" / "a.jpg", orientation=6)  # 6 = rotate 90°
        [planned] = ingest.plan(self.src, [], None, None)
        dims = ingest.process_photo(planned, self.out)
        self.assertEqual(dims, {"width": 1365, "height": 2048})  # portrait after rotation
        for size, edge in (("thumb", 480), ("display", 2048)):
            f = self.out / size / f"{planned.id}.webp"
            self.assertTrue(f.exists())
            self.assertFalse(ingest.has_gps(f))
            with Image.open(f) as im:
                self.assertEqual(max(im.size), edge)
                self.assertEqual(len(im.getexif()), 0, "web copies must carry no EXIF at all")
        self.assertTrue(ingest.has_gps(p), "the original must not be changed")

    def test_naming_uses_exif_date_and_contributor_folder(self):
        make_photo(self.src / "Saran K" / "a.jpg", taken="2026:09:12 10:15:33")
        make_photo(self.src / "Saran K" / "b.jpg", taken="2026:09:12 09:00:00")
        ids = [p.id for p in ingest.plan(self.src, [], None, None)]
        self.assertEqual(sorted(ids), ["20260912-090000_saran-k_001", "20260912-101533_saran-k_002"])

    def test_numbering_continues_and_duplicates_are_skipped(self):
        a = make_photo(self.src / "saran" / "a.jpg")
        shutil.copy(a, self.src / "saran" / "a-copy.jpg")
        existing = [{"id": "20260101-000000_saran_014", "sha256": "0" * 64}]
        planned = ingest.plan(self.src, existing, None, None)
        fresh = [p for p in planned if not p.duplicate_of]
        dupes = [p for p in planned if p.duplicate_of]
        self.assertEqual([p.id for p in fresh], ["20260912-101533_saran_015"])
        self.assertEqual(dupes[0].duplicate_of, "20260912-101533_saran_015")

    def test_already_ingested_file_is_skipped(self):
        a = make_photo(self.src / "saran" / "a.jpg")
        existing = [{"id": "20260912-101533_saran_001", "sha256": ingest.sha256_of(a)}]
        [p] = ingest.plan(self.src, existing, None, None)
        self.assertEqual(p.duplicate_of, "20260912-101533_saran_001")

    def test_scan_naming(self):
        make_photo(self.src / "a.jpg", gps=False)
        [p] = ingest.plan(self.src, [], None, 1994)
        self.assertEqual(p.id, "1994-00-00_scan_001")

    def test_dry_run_writes_nothing(self):
        make_photo(self.src / "saran" / "a.jpg")
        self.assertEqual(ingest.main(["--album", "2026-test-album", "--src", str(self.src)]), 0)
        self.assertFalse((self.album / "media.json").exists())
        self.assertFalse(self.out.exists())

    def test_apply_without_upload_writes_manifest(self):
        make_photo(self.src / "saran" / "a.jpg")
        ingest.main(["--album", "2026-test-album", "--src", str(self.src), "--apply", "--no-upload"])
        items = json.loads((self.album / "media.json").read_text("utf-8"))
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["id"], "20260912-101533_saran_001")
        self.assertEqual((item["width"], item["height"]), (2048, 1365))
        self.assertEqual(item["credit"], "saran")
        self.assertEqual(len(item["sha256"]), 64)
        self.assertTrue((self.out / "public/albums/2026-test-album/display/20260912-101533_saran_001.webp").exists())
        # Running again adds nothing.
        ingest.main(["--album", "2026-test-album", "--src", str(self.src), "--apply", "--no-upload"])
        self.assertEqual(len(json.loads((self.album / "media.json").read_text("utf-8"))), 1)


if __name__ == "__main__":
    unittest.main()
