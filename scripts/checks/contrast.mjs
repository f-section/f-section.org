// WCAG AA contrast for every text colour pair in the design tokens (DESIGN.md §6.2).
// Normal text needs 4.5:1. Large text (headings) needs 3:1.
const tokens = {
  paper: '#F6F1E7',
  card: '#FFFDF8',
  ink: '#1E2A3A',
  'ink-red': '#A23B2A',
  sepia: '#846541',
  marigold: '#E0A100',
};

// [foreground, background, minimum ratio, where it is used]
const pairs = [
  ['ink', 'paper', 4.5, 'body text'],
  ['ink', 'card', 4.5, 'text on cards'],
  ['ink-red', 'paper', 4.5, 'links'],
  ['ink-red', 'card', 4.5, 'links on cards'],
  ['sepia', 'paper', 4.5, 'dates, credits, 1992–96 labels'],
  ['sepia', 'card', 4.5, 'dates and credits on cards'],
  ['paper', 'ink', 4.5, 'active toggle and buttons'],
];

const lum = (hex) => {
  const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  const [r, g, b] = c.map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
const ratio = (a, b) => {
  const [l1, l2] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
};

let failed = false;
for (const [fg, bg, min, use] of pairs) {
  const r = ratio(tokens[fg], tokens[bg]);
  const ok = r >= min;
  if (!ok) failed = true;
  console.log(`${ok ? '✓' : '✗'} ${fg} on ${bg}: ${r.toFixed(2)}:1 (needs ${min}) ${use}`);
}
console.log(`  marigold on paper: ${ratio(tokens.marigold, tokens.paper).toFixed(2)}:1, decoration only, never text`);
if (failed) process.exit(1);
