# Building and ingest move to minnaham

**Date:** 2026-10-25
**Approved by:** Saran
**Replaces:** 2026-10-12-dev-and-ingest-on-windows.md (as the main machine)

## What changed
Development, builds and media ingest move from Saran's Windows laptop to **minnaham**, an always-on headless Ubuntu server (a Dell OptiPlex). It already has the toolchain, and two other websites were built on it.

The Windows clone at `E:\COWORK\PROJECTS\F-SECTION\f-section.org` stays as a fallback.

## Why
- The laptop sleeps or shuts down, which stops long jobs (Drive downloads, video encoding, photo processing).
- minnaham has more CPU, memory and disk, and runs around the clock.
- Linux tools are simpler to install and script.

## Notes
- minnaham gets its **own** R2 API token (same scope: Object Read & Write on `f-section-media` only), so either machine can be revoked on its own. Don't copy the laptop's token.
- Machine-only settings (rclone remotes, the Drive folder IDs) stay outside the repo, in `~/.config/`.
- Deploys still come from GitHub through Workers Builds, so wrangler is rarely needed on minnaham.
- The video masters and the song for the montage are still on the laptop in `E:\F Section\Claude outputs\`. Copy them to the NAS when convenient.
