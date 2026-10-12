/**
 * Album data: album.yaml (content collection) plus media.json (written by scripts/ingest).
 * media.json is validated here; a bad manifest stops the build.
 */
import { getCollection, type CollectionEntry } from 'astro:content';
import { z } from 'astro/zod';
import { MEMBERS_AREA_ENABLED, mediaUrl, type Era } from '../site';

const MEDIA_ID = /^(\d{8}-\d{6}|\d{4}-00-00)_[a-z0-9]+_\d{3}$/;

const mediaItem = z.object({
  id: z.string().regex(MEDIA_ID, 'Media id must be YYYYMMDD-HHMMSS_contributor_NNN or YYYY-00-00_scan_NNN'),
  type: z.enum(['photo', 'video', 'audio']),
  // Display-copy size. Audio has none.
  width: z.number().int().positive().default(1),
  height: z.number().int().positive().default(1),
  sha256: z.string().regex(/^([a-f0-9]{64})?$/),
  credit: z.string().default(''),
  taken: z.string().optional(),
  caption: z.object({ en: z.string().default(''), ta: z.string().default('') }).default({ en: '', ta: '' }),
  alt: z.object({ en: z.string().default(''), ta: z.string().default('') }).optional(),
  /** Where it was taken, from the photo's own GPS data (kept on purpose). */
  gps: z.object({ lat: z.number().min(-90).max(90), lon: z.number().min(-180).max(180) }).optional(),
  place: z.string().optional(),
  pairWith: z.string().optional(),
  /** Sample-only: render a drawn placeholder instead of loading from R2. */
  placeholder: z.boolean().optional(),
});
const manifest = z.array(mediaItem);

export type MediaItem = z.infer<typeof mediaItem>;
export type Album = CollectionEntry<'albums'> & { media: MediaItem[] };

const manifests = import.meta.glob<unknown>('/src/content/albums/*/media.json', {
  eager: true,
  import: 'default',
});

function manifestFor(slug: string): MediaItem[] {
  const raw = manifests[`/src/content/albums/${slug}/media.json`];
  if (raw === undefined) return [];
  const parsed = manifest.safeParse(raw);
  if (!parsed.success) {
    throw new Error(`src/content/albums/${slug}/media.json is invalid:\n${z.prettifyError(parsed.error)}`);
  }
  const ids = new Set<string>();
  for (const m of parsed.data) {
    if (ids.has(m.id)) throw new Error(`${slug}/media.json: duplicate id ${m.id}`);
    ids.add(m.id);
  }
  return parsed.data;
}

/** True if this item may be built into the site right now. */
export function isPublished(item: { data: { visibility: 'public' | 'members' } }): boolean {
  return item.data.visibility === 'public' || MEMBERS_AREA_ENABLED;
}

/** All albums that can be shown, newest first, with their media. */
export async function getAlbums(): Promise<Album[]> {
  const entries = await getCollection('albums');
  const albums = entries.map((entry) => {
    if (entry.data.slug !== entry.id) {
      throw new Error(`Album folder "${entry.id}" does not match its slug "${entry.data.slug}"`);
    }
    const media = manifestFor(entry.id);
    if (entry.data.cover && media.length && !media.some((m) => m.id === entry.data.cover)) {
      throw new Error(`Album ${entry.id}: cover "${entry.data.cover}" is not in media.json`);
    }
    return { ...entry, media };
  });
  return albums.filter(isPublished).sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}

export async function getAlbumsByEra(era: Era): Promise<Album[]> {
  return (await getAlbums()).filter((a) => a.data.era === era);
}

export function coverOf(album: Album): MediaItem | undefined {
  return album.media.find((m) => m.id === album.data.cover) ?? album.media[0];
}

/** Map link that opens the Maps app on phones. */
export function mapUrl(gps: { lat: number; lon: number }): string {
  return `https://www.google.com/maps/search/?api=1&query=${gps.lat},${gps.lon}`;
}

/** R2 keys follow `<visibility>/albums/<slug>/<size>/<id>.webp` (see scripts/ingest). */
export function photoUrl(album: Album, item: MediaItem, size: 'thumb' | 'display'): string {
  return mediaUrl(`${album.data.visibility}/albums/${album.id}/${size}/${item.id}.webp`);
}
