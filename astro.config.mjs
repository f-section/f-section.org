// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

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
  vite: {
    plugins: [tailwindcss()],
  },
});
