/**
 * Content collections and schemas (DESIGN.md §10).
 * A wrong field in any content file stops the build.
 * Album media manifests (media.json) are validated in src/lib/media.ts.
 */
import { defineCollection, reference } from 'astro:content';
import { glob, file } from 'astro/loaders';
import { z } from 'astro/zod';
import { ERAS } from './site';

const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const ALBUM_SLUG = /^\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*$/;

/** `{ en, ta }` pair. English is required; empty Tamil falls back to English. */
const pair = z.object({
  en: z.string().min(1),
  ta: z.string().nullish().transform((v) => v ?? ''),
});
/** Same, but English may also be empty (optional text). */
const optionalPair = z
  .object({
    en: z.string().nullish().transform((v) => v ?? ''),
    ta: z.string().nullish().transform((v) => v ?? ''),
  })
  .default({ en: '', ta: '' });

/** Public-first (D-14): everything is public unless marked members. */
const visibility = z.enum(['public', 'members']).default('public');

/** An R2 object key, e.g. `public/video/x-720.mp4`. Never a full URL. */
const r2Key = z
  .string()
  .regex(/^(public|members)\/[A-Za-z0-9._\/-]+$/, 'Must be an R2 key starting with public/ or members/');

/** Members-only items must point only at members/ keys (DESIGN.md §7, rule 6). */
function keysMatchVisibility(vis: 'public' | 'members', keys: (string | null | undefined)[]) {
  return keys.every((k) => !k || k.startsWith(`${vis}/`));
}

const places = defineCollection({
  loader: file('src/content/places.yaml'),
  schema: z.object({
    id: z.string().regex(SLUG),
    name: pair,
    description: optionalPair,
  }),
});

const albums = defineCollection({
  loader: glob({
    pattern: '*/album.yaml',
    base: './src/content/albums',
    generateId: ({ entry }) => entry.split('/')[0],
  }),
  schema: z.object({
    slug: z.string().regex(ALBUM_SLUG, 'Album slug must look like YYYY-event-topic'),
    era: z.enum(ERAS),
    date: z.coerce.date(),
    title: pair,
    summary: optionalPair,
    location: optionalPair,
    visibility,
    cover: z.string().optional(),
    places: z.array(reference('places')).default([]),
  }),
});

const videos = defineCollection({
  loader: glob({ pattern: '*.yaml', base: './src/content/videos' }),
  schema: z
    .object({
      slug: z.string().regex(ALBUM_SLUG),
      era: z.enum(ERAS),
      title: pair,
      summary: optionalPair,
      visibility,
      duration: z.string().regex(/^\d{1,2}:\d{2}(:\d{2})?$/),
      files: z.object({ '1080': r2Key.optional(), '720': r2Key }),
      poster: r2Key,
      subtitles: z.object({ en: r2Key.nullish(), ta: r2Key.nullish() }).default({ en: null, ta: null }),
    })
    .refine(
      (v) =>
        keysMatchVisibility(v.visibility, [v.files['1080'], v.files['720'], v.poster, v.subtitles.en, v.subtitles.ta]),
      { message: 'Every file key must start with the visibility prefix (public/ or members/)', path: ['files'] },
    ),
});

const arivumalar = defineCollection({
  loader: glob({ pattern: '*.yaml', base: './src/content/arivumalar' }),
  schema: z
    .object({
      // YYYY-MM, or volNN-issNN if the originals carry numbers (O-4).
      id: z.string().regex(/^(\d{4}-(0[1-9]|1[0-2])|vol\d{2}-iss\d{2}|\d{4})$/),
      kind: z.enum(['archive', 'annual']),
      year: z.number().int().min(1992).max(2100),
      title: pair,
      visibility,
      pages: z.number().int().min(1),
      pdf: r2Key.optional(),
      contents: z
        .array(z.object({ page: z.number().int().min(1), title: optionalPair.or(z.string()), author: z.string().default('') }))
        .default([]),
      editors: z.array(z.string()).default([]),
    })
    .refine((v) => keysMatchVisibility(v.visibility, [v.pdf]), {
      message: 'pdf key must start with the visibility prefix',
      path: ['pdf'],
    }),
});

const people = defineCollection({
  loader: glob({ pattern: '*.yaml', base: './src/content/people' }),
  schema: z.object({
    slug: z.string().regex(SLUG),
    name: pair,
    section: z.string().regex(/^[A-Z]$/),
    visibility,
    photo_1996: r2Key.optional(),
    photo_2026: r2Key.optional(),
    bio: optionalPair,
  }),
});

const memoriam = defineCollection({
  loader: glob({ pattern: '*.yaml', base: './src/content/memoriam' }),
  schema: z.object({
    slug: z.string().regex(SLUG),
    name: pair,
    years: z.string(),
    photo: r2Key.optional(),
    tribute: optionalPair,
    visibility,
  }),
});

export const collections = { places, albums, videos, arivumalar, people, memoriam };
