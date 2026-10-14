import { getCollection } from 'astro:content';
import { isPublished } from './media';
import type { Era } from '../site';

/** Published videos, in era order then by slug (slugs start with the year). */
export async function getVideos(era?: Era) {
  const all = (await getCollection('videos')).filter(isPublished);
  return all
    .filter((v) => !era || v.data.era === era)
    .sort((a, b) => b.data.slug.localeCompare(a.data.slug));
}
