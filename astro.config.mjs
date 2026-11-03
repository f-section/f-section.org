// @ts-check
import { readFileSync } from 'node:fs';
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';
import { satteri } from '@astrojs/markdown-satteri';

// Picture sizes for the Arivu Malar e-book, written by scripts/arivumalar/media.py.
const ebookImg = JSON.parse(readFileSync(new URL('./src/lib/ebook-img.json', import.meta.url), 'utf8'));
const MEDIA_BASE = 'https://media.f-section.org';

/**
 * `![](r2:public/…)` in the e-book Markdown. The `r2:` scheme keeps Astro's image
 * pipeline out of the way (these pictures live in R2, not in the repo). Here each one
 * gets its real address and its real size, so the page reserves the right space before
 * it loads, and is wrapped in the same `a[data-lb-item]` link the gallery uses, so the
 * photo viewer picks it up and a tap still opens the picture with JavaScript off.
 *
 * The `after` hook then says how each picture sits in the piece, which depends on the
 * block that follows it.
 */
/** @type {import('satteri').HastPluginDefinition} */
const ebookPictures = {
  name: 'f-section:ebook-pictures',
  element: {
    filter: ['img'],
    visit(node, ctx) {
      const src = String(node.properties?.src ?? '');
      if (!src.startsWith('r2:')) return;
      const key = src.slice(3);
      const size = ebookImg[key];
      if (!size) throw new Error(`${key} has no size in src/lib/ebook-img.json — run scripts/arivumalar/media.py`);
      const url = `${MEDIA_BASE}/${key}`;
      ctx.setProperty(node, 'src', url);
      ctx.setProperty(node, 'width', size[0]);
      ctx.setProperty(node, 'height', size[1]);
      ctx.setProperty(node, 'loading', 'lazy');
      ctx.setProperty(node, 'decoding', 'async');
      ctx.wrapNode(node, {
        type: 'element',
        tagName: 'a',
        properties: { href: url, class: 'block', 'data-lb-item': '' },
        children: [],
      });
    },
  },
  /**
   * How each picture sits on the reading page (DESIGN.md §10.4). It depends on what
   * follows it, which CSS cannot ask -- `:has()` does not nest -- so the class is
   * decided here, where the blocks of the piece are in hand:
   *   `eb-flow`  a paragraph follows, so the picture sits in the text and the text
   *              runs on beside it, left and right down the page
   *   `eb-pair`  the next block is another picture: the two stand side by side
   *   `eb-wide`  a heading, a quote, a break or the end of the piece follows, so the
   *              picture stands on its own, centred and larger
   */
  after(root, ctx) {
    const kids = /** @type {import('hast').Element[]} */ (root.children.filter((n) => n.type === 'element'));
    /** @param {import('hast').Element | undefined} n */
    const isPicture = (n) => {
      if (n?.tagName !== 'p') return false;
      const inner = n.children.filter((c) => c.type === 'element');
      const only = inner.length === 1 ? /** @type {import('hast').Element} */ (inner[0]) : undefined;
      return !!only && (only.tagName === 'img' || only.properties?.['data-lb-item'] !== undefined);
    };
    let flowed = 0;
    for (let i = 0; i < kids.length; i++) {
      if (!isPicture(kids[i])) continue;
      const next = kids[i + 1];
      if (next && isPicture(next)) {
        ctx.setProperty(kids[i], 'class', 'eb-pic eb-pair eb-pair-first');
        ctx.setProperty(next, 'class', 'eb-pic eb-pair');
        i++; // the pair is placed; the second one is not a picture looking for a side
        continue;
      }
      if (next?.tagName === 'p') {
        ctx.setProperty(kids[i], 'class', `eb-pic eb-flow ${flowed++ % 2 ? 'eb-left' : 'eb-right'}`);
        continue;
      }
      ctx.setProperty(kids[i], 'class', 'eb-pic eb-wide');
    }
  },
};

// Fully static site (DESIGN.md §7). English at `/`, Tamil at `/ta/`.
// Language routing is done with a `[...lang]` rest parameter in src/pages,
// so each page is written once and built for both languages.
export default defineConfig({
  site: 'https://f-section.org',
  output: 'static',
  trailingSlash: 'always',
  build: { format: 'directory' },
  // The site is open to search engines (O-2 decided 2026-10-12). The internal style guide is left out.
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/styleguide/'),
      i18n: { defaultLocale: 'en', locales: { en: 'en-IN', ta: 'ta-IN' } },
    }),
  ],
  markdown: {
    processor: satteri({ hastPlugins: [ebookPictures] }),
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
