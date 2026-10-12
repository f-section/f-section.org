// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// Fully static site (DESIGN.md §7). English at `/`, Tamil at `/ta/`.
// Language routing is done with a `[...lang]` rest parameter in src/pages,
// so each page is written once and built for both languages.
export default defineConfig({
  site: 'https://f-section.org',
  output: 'static',
  trailingSlash: 'always',
  build: { format: 'directory' },
  vite: {
    plugins: [tailwindcss()],
  },
});
