# Development and ingest run on Windows

> **Replaced on 2026-10-25** by `2026-10-25-build-on-minnaham.md`. The Windows PC is now the fallback.

**Date:** 2026-10-12
**Approved by:** Saran
**Affects:** DESIGN.md §7, §8.1, §16

## What changed
Development and the ingest script now run on Saran's Windows PC, not the Linux machine (`minnaham`). The working copy of the repo is at `E:\COWORK\PROJECTS\F-SECTION\f-section.org`, next to Saran's other projects. The NAS is reached as a mapped drive.

## Why
It keeps all of Saran's projects in one folder structure, and Git, Node, Python, `gh` and `wrangler` are already installed on the PC.

## Notes
- GitHub stays the single source of truth. The repo can still be cloned on `minnaham` at any time.
- `.gitattributes` forces LF line endings so Windows and Cloudflare's Linux builds agree.
- The ingest script must stay cross-platform (Windows and Linux).
- The ingest script needs `rclone` and `ffmpeg` on the PC. Install them with winget when the first real album is ingested.
