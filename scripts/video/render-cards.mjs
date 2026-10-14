// Render the montage title cards (scripts/video/cards/*.html) to 1920 × 1080 PNGs with headless Chrome,
// which shapes Tamil correctly. Output: scripts/video/out/cards/*.png (git-ignored).
//
// Usage: node scripts/video/render-cards.mjs --cover "E:/F Section/Claude outputs/Montage cards (draft)/arivumalar-final-cover.webp"
import { execFileSync } from 'node:child_process';
import { copyFileSync, existsSync, mkdirSync, readdirSync } from 'node:fs';
import { dirname, extname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const cardsDir = join(here, 'cards');

const arg = (name) => {
  const i = process.argv.indexOf(name);
  return i > -1 ? process.argv[i + 1] : undefined;
};
const cover = arg('--cover');
// --scale 2 renders 3840 × 2160 (for a smooth slow zoom in the video); output goes to out/cards@2x.
const scale = Number(arg('--scale') ?? 1);
if (cover) {
  mkdirSync(join(cardsDir, 'assets'), { recursive: true });
  // Keep the extension (.webp, .jpeg …); 02-arivumalar.html expects arivumalar-cover.webp.
  copyFileSync(resolve(cover), join(cardsDir, 'assets', `arivumalar-cover${extname(cover).toLowerCase()}`));
}

const chrome = [
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
].find(existsSync);
if (!chrome) throw new Error('Chrome or Edge not found');
const outDir = join(here, 'out', scale === 1 ? 'cards' : `cards@${scale}x`);
mkdirSync(outDir, { recursive: true });

for (const file of readdirSync(cardsDir).filter((f) => f.endsWith('.html'))) {
  const png = join(outDir, file.replace(/\.html$/, '.png'));
  execFileSync(chrome, [
    '--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
    `--force-device-scale-factor=${scale}`, '--window-size=1920,1080', '--virtual-time-budget=15000',
    `--screenshot=${png}`, pathToFileURL(join(cardsDir, file)).href,
  ], { stdio: 'ignore' });
  console.log(`✓ ${png}`);
}
