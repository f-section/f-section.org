// Lists every piece of text that still needs Tamil (DESIGN.md §5). Report only; never fails.
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import YAML from 'yaml';

const todo = [];

const ta = JSON.parse(readFileSync('src/i18n/ta.json', 'utf8'));
// Keys Saran chose to keep in English on Tamil pages (logo, tagline, footer).
const englishOnly = new Set(JSON.parse(readFileSync('src/i18n/english-only.json', 'utf8')));
for (const [k, v] of Object.entries(ta)) if (!v && !englishOnly.has(k)) todo.push(`src/i18n/ta.json  ${k}`);

function* files(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) yield* files(p);
    else if (/\.(ya?ml|json)$/.test(name)) yield p;
  }
}

// Any object shaped like { en: "text", ta: "" } is a bilingual pair missing Tamil.
function scan(node, file, path) {
  if (Array.isArray(node)) return node.forEach((v, i) => scan(v, file, `${path}[${i}]`));
  if (node && typeof node === 'object') {
    if ('en' in node && 'ta' in node && typeof node.en === 'string' && node.en && !node.ta) {
      todo.push(`${file}  ${path || '(root)'}: "${node.en.slice(0, 60)}"`);
      return;
    }
    for (const [k, v] of Object.entries(node)) scan(v, file, path ? `${path}.${k}` : k);
  }
}

for (const file of files('src/content')) {
  const text = readFileSync(file, 'utf8');
  const data = file.endsWith('.json') ? JSON.parse(text) : YAML.parse(text);
  scan(data, file.replaceAll('\\', '/'), '');
}

if (todo.length) {
  console.log(`\nTamil still needed (${todo.length}). English is shown until it is filled in:`);
  for (const line of todo) console.log(`  · ${line}`);
} else {
  console.log('✓ Tamil: nothing missing');
}
