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

    def test_photo_copies_are_upright_and_display_keeps_location(self):
        p = make_photo(self.src / "saran" / "a.jpg", orientation=6)  # 6 = rotate 90°
        original_bytes = p.read_bytes()
        [planned] = ingest.plan(self.src, [], None, None)
        fields = ingest.process_photo(planned, self.out)
        self.assertEqual((fields["width"], fields["height"]), (1365, 2048))  # portrait after rotation
        # 10°45'30"N 78°49'E (the fixture's fake coordinates)
        self.assertEqual(fields["gps"], {"lat": 10.758333, "lon": 78.816667})

        display = self.out / "display" / f"{planned.id}.webp"
        thumb = self.out / "thumb" / f"{planned.id}.webp"
        with Image.open(display) as im:
            self.assertEqual(max(im.size), 2048)
            exif = im.getexif()
            self.assertTrue(ingest.has_gps(display), "display copy keeps GPS")
            self.assertEqual(exif.get_ifd(ingest.EXIF_IFD).get(ingest.EXIF_DATETIME_ORIGINAL), "2026:09:12 10:15:33")
            self.assertNotEqual(exif.get(0x0112), 6, "orientation must be reset after rotating")
        with Image.open(thumb) as im:
            self.assertEqual(max(im.size), 480)
            self.assertEqual(len(im.getexif()), 0, "thumbnails carry no metadata")
        self.assertEqual(p.read_bytes(), original_bytes, "the original must not be changed")

    def test_photo_without_gps_has_no_gps_field(self):
        make_photo(self.src / "saran" / "a.jpg", gps=False)
        [planned] = ingest.plan(self.src, [], None, None)
        self.assertNotIn("gps", ingest.process_photo(planned, self.out))

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
        self.assertEqual(item["gps"], {"lat": 10.758333, "lon": 78.816667})
        self.assertTrue((self.out / "public/albums/2026-test-album/display/20260912-101533_saran_001.webp").exists())
        # Running again adds nothing.
        ingest.main(["--album", "2026-test-album", "--src", str(self.src), "--apply", "--no-upload"])
        self.assertEqual(len(json.loads((self.album / "media.json").read_text("utf-8"))), 1)

    def test_curated_order_survives_a_second_ingest(self):
        """media.json order is display order and may be hand-curated, so a later
        ingest must append rather than reshuffle (2026-10-26)."""
        make_photo(self.src / "saran" / "a.jpg", taken="2026:09:12 10:15:33")
        make_photo(self.src / "saran" / "b.jpg", taken="2026:09:12 09:00:00")
        ingest.main(["--album", "2026-test-album", "--src", str(self.src), "--apply", "--no-upload"])

        # Hand-curate: put the later photo first, as the campus album does with the gate.
        path = self.album / "media.json"
        items = json.loads(path.read_text("utf-8"))
        items.reverse()
        curated = [m["id"] for m in items]
        path.write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")

        # A new photo arrives and ingest runs again.
        make_photo(self.src / "saran" / "c.jpg", taken="2026:09:12 08:00:00")
        ingest.main(["--album", "2026-test-album", "--src", str(self.src), "--apply", "--no-upload"])

        after = [m["id"] for m in json.loads(path.read_text("utf-8"))]
        self.assertEqual(after[:2], curated, "curated order was reshuffled")
        self.assertEqual(len(after), 3, "the new photo should be appended")
        self.assertNotIn(after[2], curated)

    def test_gps_tags_with_no_fix_are_dropped_not_written_as_nan(self):
        """A camera can write GPS tags with 0/0 rationals when it never got a fix.
        float(IFDRational(0, 0)) is nan, which used to reach media.json as bare NaN
        and break the build, because that is not valid JSON (2026-10-26)."""
        from PIL import TiffImagePlugin

        path = self.src / "saran" / "nofix.jpg"
        make_photo(path, gps=False)
        im = Image.open(path)
        exif = im.getexif()
        exif.get_ifd(ingest.EXIF_IFD)[ingest.EXIF_DATETIME_ORIGINAL] = "2026:09:12 10:15:33"
        g = exif.get_ifd(ingest.GPS_IFD)
        zero = TiffImagePlugin.IFDRational(0, 0)
        g[1], g[2] = "", (zero, zero, zero)
        g[3], g[4] = "", (zero, zero, zero)
        im.save(path, exif=exif)

        self.assertIsNone(ingest.photo_gps(path), "GPS with no fix should be dropped")

        ingest.main(["--album", "2026-test-album", "--src", str(self.src), "--apply", "--no-upload"])
        raw = (self.album / "media.json").read_text("utf-8")
        self.assertNotIn("NaN", raw)
        json.loads(raw)  # strict parsers must accept it


if __name__ == "__main__":
    unittest.main()
