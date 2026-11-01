/**
 * The Arivu Malar e-book: issues, their reading pages and the `அன்றும் இன்றும்` profiles
 * (DESIGN.md §10.4). The content files are written by scripts/arivumalar/extract.py out
 * of the Claude Design export; the Tamil in them is verbatim.
 */
import { getCollection, type CollectionEntry } from 'astro:content';
import { href, type Lang } from '../i18n';
import { mediaUrl } from '../site';
import { getAlbums, photoUrl, isPublished, type Album, type MediaItem } from './media';
import sizes from './ebook-img.json';

export type Issue = CollectionEntry<'arivumalar'>;
export type Section = CollectionEntry<'arivumalarSections'>;
export type Person = CollectionEntry<'arivumalarPeople'>;
export type Photo = { key: string; alt: string; caption?: string };

/** Issues that can be shown, newest first. */
export async function getIssues(): Promise<Issue[]> {
  const issues = (await getCollection('arivumalar')).filter(isPublished);
  return issues.sort((a, b) => b.data.year - a.data.year);
}

/**
 * The reading pages, in the order set by `order` in the issue's YAML file — the one
 * place the web order is decided. A section missing from that list, or listed but not
 * written, stops the build rather than quietly disappearing from the book.
 */
export async function sectionsOf(issue: Issue): Promise<Section[]> {
  const all = (await getCollection('arivumalarSections')).filter((s) => s.data.issue === issue.id);
  const bySlug = new Map(all.map((s) => [s.data.slug, s]));
  const ordered = issue.data.order.map((slug) => {
    const section = bySlug.get(slug);
    if (!section) throw new Error(`arivumalar ${issue.id}: order lists "${slug}", which has no section file`);
    return section;
  });
  const left = all.filter((s) => !issue.data.order.includes(s.data.slug)).map((s) => s.data.slug);
  if (left.length) throw new Error(`arivumalar ${issue.id}: not in order, so unreachable: ${left.join(', ')}`);
  return ordered;
}

/** The people, in the book's own numbered order. */
export async function peopleOf(issue: Issue): Promise<Person[]> {
  const people = (await getCollection('arivumalarPeople')).filter((p) => p.id.startsWith(`${issue.id}/`));
  return people.sort((a, b) => a.data.order - b.data.order);
}

export function issueHref(lang: Lang, issue: Issue): string {
  return href(lang, `/arivumalar/${issue.id}/`);
}
export function sectionHref(lang: Lang, issue: Issue, section: Section): string {
  return href(lang, `/arivumalar/${issue.id}/${section.data.slug}/`);
}
export function personHref(lang: Lang, issue: Issue, person: Person): string {
  return href(lang, `/arivumalar/${issue.id}/people/${person.data.slug}/`);
}

/** The picture's size in pixels, recorded by scripts/arivumalar/media.py. */
export function imgSize(key: string): { width: number; height: number } | undefined {
  const wh = (sizes as Record<string, number[]>)[key];
  return wh && wh.length === 2 ? { width: wh[0], height: wh[1] } : undefined;
}

/** A picture of the book, ready to put in the page. */
export function picture(photo: Photo) {
  return { src: mediaUrl(photo.key), alt: photo.alt, ...imgSize(photo.key) };
}

/**
 * Text of the book itself: a title, a name. The magazine is Tamil, so the English
 * pages print the Tamil words too (Saran, 2026-10-31) — only people's names have a
 * Latin spelling, and `taPair` leaves `en` empty where there is none.
 */
export function words(pair: { ta: string; en?: string | null }, lang: Lang): string {
  return lang === 'en' && pair.en ? pair.en : pair.ta;
}

/** The names under a page's title, in the language of the page. */
export function authorsOf(section: Section, lang: Lang): string {
  return section.data.authors.map((a) => words(a, lang)).join(' · ');
}

/** Megabytes as a browser shows them, for the download link. */
export function megabytes(bytes: number): string {
  return `${(bytes / 1e6).toFixed(1)} MB`;
}

export type EventPhoto = {
  src: string;
  width: number;
  height: number;
  album: Album;
  item: MediaItem;
};

/**
 * The photograph of them speaking on release night. It points at a picture already in a
 * gallery album (Saran, 2026-10-31), so the same object serves both pages and nothing is
 * uploaded twice. A tag that names a missing album or photo stops the build.
 */
export async function eventPhotosOf(people: Person[]): Promise<Map<string, EventPhoto>> {
  const tagged = people.filter((p) => p.data.photo_event);
  if (!tagged.length) return new Map();
  const albums = new Map((await getAlbums()).map((a) => [a.id, a]));
  const out = new Map<string, EventPhoto>();
  for (const person of tagged) {
    const tag = person.data.photo_event!;
    const album = albums.get(tag.album);
    if (!album) throw new Error(`${person.id}: photo_event album "${tag.album}" is not a published album`);
    const item = album.media.find((m) => m.id === tag.id);
    if (!item) throw new Error(`${person.id}: photo_event "${tag.id}" is not in ${tag.album}/media.json`);
    out.set(person.id, {
      src: photoUrl(album, item, 'display'),
      width: item.width,
      height: item.height,
      album,
      item,
    });
  }
  return out;
}

/** Where an album's own page lives, for the link under the release-night photograph. */
export function albumHref(lang: Lang, album: Album, eraSlugOf: (era: Album['data']['era']) => string): string {
  return href(lang, `/gallery/${eraSlugOf(album.data.era)}/${album.id}/`);
}
