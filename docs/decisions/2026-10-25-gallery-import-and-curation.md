# Importing and curating the 30th reunion gallery

**Date:** 2026-10-25
**Approved by:** Saran
**Affects:** DESIGN.md §4.4, §8.1; RUNBOOK; scripts/ingest

## Where the photos come from
Friends uploaded their 30th reunion photos and videos to a Google Drive folder owned by Saran, with one subfolder per person (for example `11-Saravanan`, `07 - Mohanraj`). Not everyone uploaded. Some folders mix photos and videos, which is fine.

The folder links are **private**: Saran's Drive also holds personal material. They never go in this public repo. They live in a local config file on the build machine, outside git.

## Access: read-only
- Claude reads the folder through an rclone Google Drive remote, limited to the reunion photo folder, with **read-only** access. Nothing on the Drive is renamed, moved or deleted.
- Friends keep seeing their own uploads exactly as they left them.

## Renaming: in staging, never on the Drive
Files are renamed only in the work area on minnaham (see "Work area" below):

> **Superseded on 2026-10-26** by `2026-10-26-media-ids-stay-short.md`: there is no
> place-or-event segment. The name is `<YYYYMMDD>-<HHMMSS>_<who>_<NNN>.<ext>`, and the place is
> optional metadata in `media.json`. The rest of this section still applies.

```
<YYYYMMDD>-<HHMMSS>_<who>_<NNN>.<ext>
20261003-184212_saravanan_001.jpg
```

- **Date and time:** from EXIF first. For copies with no EXIF (WhatsApp forwards), from the file name (`IMG-20261003-WA0012`), then the Drive date.
- **Who:** the contributor's folder name, lowercased (`07 - Mohanraj` → `mohanraj`).
- **Place or event:** from GPS matched to `places.yaml`, then from the reunion schedule by time. Claude judges what is quickest: ask Saran, or make a sensible guess.
- **No content labels** in names, and no titles or captions in the gallery.
  - **Amended 2026-10-26:** one narrow exception. The five department group photos in the campus
    album carry the department as a caption (`Production`, `Civil`, `Mechanical`, `Electrical`,
    `Metallurgy`), because the caption is the whole point of those pictures: classmates look for
    their own department. Every other photo stays caption-free. This is an exception, not a change
    of policy: do not caption anything else without asking Saran.

A **manifest** (CSV) links each new name to the Drive path, Drive file ID, original name and SHA-256 hash. It stays with the originals in `/mnt/data/f-section/originals/`, not in the repo, because it holds Drive IDs.

## Work area: minnaham's local disk, not the NAS
The NAS is slow, and working straight off it has caused problems before. All downloading, converting, renaming, reviewing and ingest happen on minnaham's local disk, in **`/mnt/data/f-section`** (about 1 TB free):

```
/mnt/data/f-section/
  drive/       read-only copy of the Drive folder, as downloaded (original names)
  work/        converted and renamed files, grouped by event
  originals/   <album-slug>/ full-size originals of the picks, with manifest.csv (master copy)
  review/      the contact sheet for Saran (not published)
  out/         ingest output (web copies) before upload to R2
  masters/     video masters, such as the 30th reunion montage and its song
```

The NAS is only a **backup and archive** target. Copy finished folders to it with rclone or rsync, as a single bulk copy and never as a working directory. This is also where photos and videos retired from the site go.

## Curation rules
- **Videos: tight.** Only a few short, strong clips. Each one costs storage.
- **Photos: lighter, but no repeats.** Many friends shot the same moments. For each place or event, keep only the few best photos. It is fine to drop most photos and end up with a small gallery.
- **Prefer natural moments:** friends talking and laughing, unaware of the camera, over posed shots of people looking at the lens.
- **Quality first:** sharp, well-lit and well-framed. Drop blurry shots, near-identical bursts and screenshots.
- **Mohanraj's folder** (`07 - Mohanraj`) is professional quality. Start there and draw on it heavily.
- Exact duplicates across folders are removed, keeping the copy with the most metadata.
- Claude does the first pass. Saran approves the final picks on a review page (a contact sheet that is not published) before anything is ingested.

## Storage budget
The R2 free tier is 10 GB, and it is not unlimited. Curation keeps us well under it. When storage approaches 8 GB, Saran will move older photos and videos off the site to the NAS archive. Keep that path in mind: albums must stay easy to retire one at a time. The originals stay in `/mnt/data/f-section/originals/<album-slug>/`, backed up to the NAS, and never go to R2.

## Build machine
From now on, building and ingest run on **minnaham**, Saran's always-on Ubuntu server (a Dell OptiPlex). See `2026-10-25-build-on-minnaham.md`.
