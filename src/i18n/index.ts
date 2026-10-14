import en from './en.json';
import ta from './ta.json';
import englishOnly from './english-only.json';

export const LANGS = ['en', 'ta'] as const;
export type Lang = (typeof LANGS)[number];
export const DEFAULT_LANG: Lang = 'en';

export type UiKey = keyof typeof en;
const ui: Record<Lang, Record<string, string>> = { en, ta };

/** A bilingual content field: `{ en: "...", ta: "..." }`. */
export type Pair = { en: string; ta?: string | null };

/**
 * Keys shown in English on every page, by Saran's choice (2026-10-14): the
 * "F Section" logo, the tagline and the footer line. Listed in english-only.json.
 */
const ENGLISH_ONLY = new Set<string>(englishOnly);

/** Interface string. Empty Tamil falls back to English (DESIGN.md §5). */
export function t(lang: Lang, key: UiKey): string {
  if (ENGLISH_ONLY.has(key)) return ui.en[key];
  return ui[lang][key] || ui.en[key];
}

/** The language the text from `t()` is actually in (English when Tamil is missing). */
export function tLang(lang: Lang, key: UiKey): Lang {
  return lang === 'ta' && !ENGLISH_ONLY.has(key) && ui.ta[key] ? 'ta' : 'en';
}

/** Content text. Empty Tamil falls back to English. */
export function pick(pair: Pair | undefined | null, lang: Lang): string {
  if (!pair) return '';
  if (lang === 'ta' && pair.ta) return pair.ta;
  return pair.en;
}

/** True when the text shown is the English fallback on a Tamil page. */
export function isFallback(pair: Pair | undefined | null, lang: Lang): boolean {
  return lang === 'ta' && !!pair && !pair.ta;
}

/** Value for the `[...lang]` route param: undefined for English, 'ta' for Tamil. */
export function langParam(lang: Lang): string | undefined {
  return lang === DEFAULT_LANG ? undefined : lang;
}

/** Read the language from the `[...lang]` route param. */
export function langFromParam(param: string | undefined): Lang {
  return param === 'ta' ? 'ta' : 'en';
}

/** getStaticPaths entries for both languages, with optional extra params/props. */
export function bothLangs<P extends Record<string, string>, R extends Record<string, unknown>>(
  params: P = {} as P,
  props: R = {} as R,
) {
  return LANGS.map((lang) => ({ params: { lang: langParam(lang), ...params }, props: { ...props } }));
}

/** Build a site path in a language. `href('ta', '/gallery/')` → `/ta/gallery/`. */
export function href(lang: Lang, path = '/'): string {
  const clean = '/' + path.replace(/^\/+/, '');
  const withSlash = /\.[a-z0-9]+$/i.test(clean) || clean.endsWith('/') ? clean : clean + '/';
  return lang === DEFAULT_LANG ? withSlash : `/${lang}${withSlash}`;
}

/** Strip the language prefix from a pathname: `/ta/gallery/` → `/gallery/`. */
export function basePath(pathname: string): string {
  const stripped = pathname.replace(/^\/ta(\/|$)/, '/');
  return stripped || '/';
}

/** Same page in the other language (the toggle never jumps to the home page). */
export function switchHref(pathname: string, to: Lang): string {
  return href(to, basePath(pathname));
}
