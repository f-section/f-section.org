// No phone numbers anywhere in content or interface text (DESIGN.md §13.6).
// Street addresses cannot be detected reliably; review those by hand.
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const ROOTS = ['src/content', 'src/i18n', 'src/pages', 'src/components'];
const PHONE = [
  // Indian mobile, with or without +91 / 0 prefix: 98765 43210, +91-9876543210
  /(?<![\w-])(?:\+91[\s-]?|0)?[6-9]\d{4}[\s-]?\d{5}(?![\w-])/,
  // Any number written with a country code: +1 919 555 0100, +44 20 7946 0958
  /(?<![\w])\+\d{1,3}[\s-]?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}(?![\w-])/,
];

function* walk(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) yield* walk(p);
    else if (/\.(ya?ml|json|md|mdx|astro|ts)$/.test(name)) yield p;
  }
}

const hits = [];
for (const root of ROOTS) {
  for (const file of walk(root)) {
    readFileSync(file, 'utf8')
      .split(/\r?\n/)
      .forEach((line, i) => {
        if (/sha256/.test(line)) return;
        if (PHONE.some((re) => re.test(line))) hits.push(`${file}:${i + 1}: ${line.trim().slice(0, 100)}`);
      });
  }
}

if (hits.length) {
  console.error(`✗ Possible phone numbers (not allowed anywhere on the site):\n  ${hits.join('\n  ')}`);
  process.exit(1);
}
console.log('✓ no phone numbers found');
