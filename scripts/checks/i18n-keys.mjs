// Every interface string must exist in both en.json and ta.json (CLAUDE.md rule 5).
import { readFileSync } from 'node:fs';

const load = (l) => JSON.parse(readFileSync(new URL(`../../src/i18n/${l}.json`, import.meta.url), 'utf8'));
const en = load('en');
const ta = load('ta');

const missingInTa = Object.keys(en).filter((k) => !(k in ta));
const missingInEn = Object.keys(ta).filter((k) => !(k in en));
const emptyEn = Object.entries(en).filter(([, v]) => !v).map(([k]) => k);

let failed = false;
if (missingInTa.length) {
  console.error(`✗ Keys missing from ta.json (add them, value "" is fine):\n  ${missingInTa.join('\n  ')}`);
  failed = true;
}
if (missingInEn.length) {
  console.error(`✗ Keys in ta.json but not en.json:\n  ${missingInEn.join('\n  ')}`);
  failed = true;
}
if (emptyEn.length) {
  console.error(`✗ Empty English values:\n  ${emptyEn.join('\n  ')}`);
  failed = true;
}
if (failed) process.exit(1);
console.log(`✓ i18n: ${Object.keys(en).length} keys in both en.json and ta.json`);
