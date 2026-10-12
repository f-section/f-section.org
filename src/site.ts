/** Site-wide settings. */

/** R2 bucket `f-section-media`, served through a custom domain (DESIGN.md §7). */
export const MEDIA_BASE = 'https://media.f-section.org';

/** Default link-preview image (1200 × 630). Uploaded to R2, not committed to git. */
export const DEFAULT_OG_IMAGE = `${MEDIA_BASE}/public/site/og-default.jpg`;

/**
 * Email shown for takedown requests. Where the notice appears is open (O-7).
 * While this is null, the footer shows no takedown line.
 */
export const TAKEDOWN_EMAIL: string | null = null;

/**
 * Members-only content is not built into the site until the login exists
 * (Phase 2, O-1). Keep this false until Cloudflare Access protects /members/*.
 */
export const MEMBERS_AREA_ENABLED = false;

/** Search engines are asked not to index the site (D-10, O-2). */
export const NOINDEX = true;

export const ERAS = ['1992-96', 'in-between', '2016-20th', '2026-30th', '2027+'] as const;
export type Era = (typeof ERAS)[number];

/** URL segment for an era. `2027+` is not URL-friendly. */
export function eraSlug(era: Era): string {
  return era === '2027+' ? 'after-30' : era;
}

/** Eras shown with the sepia "ink then" frame (DESIGN.md §6.1). */
export function isThen(era: Era): boolean {
  return era === '1992-96';
}

/** Public URL for an R2 object key such as `public/albums/<slug>/thumb/<id>.webp`. */
export function mediaUrl(key: string): string {
  return `${MEDIA_BASE}/${key.replace(/^\/+/, '')}`;
}
