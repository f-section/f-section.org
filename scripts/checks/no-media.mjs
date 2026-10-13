// Fails if any photo, video, audio or scan is tracked in git (DESIGN.md D-04).
// Only files under public/icons/ are allowed. Also blocks any file over 5 MB.
import { execSync } from 'node:child_process';
import { statSync } from 'node:fs';

const MEDIA = /\.(jpe?g|png|gif|webp|avif|hei[cf]|tiff?|bmp|raw|cr2|nef|arw|dng|psd|mp4|m4v|mov|avi|mkv|webm|3gp|mts|wav|mp3|m4a|aac|flac|ogg|opus|pdf|zip)$/i;
const ALLOWED = /^public\/icons\//;
const MAX_BYTES = 5 * 1024 * 1024;

const files = execSync('git ls-files -z', { encoding: 'utf8' }).split('\0').filter(Boolean);
const media = files.filter((f) => MEDIA.test(f) && !ALLOWED.test(f));
const large = files.filter((f) => {
  try {
    return statSync(f).size > MAX_BYTES;
  } catch {
    return false;
  }
});

if (media.length || large.length) {
  if (media.length) console.error(`✗ Media files must not be in git (upload them to R2 with scripts/ingest):\n  ${media.join('\n  ')}`);
  if (large.length) console.error(`✗ Files over 5 MB:\n  ${large.join('\n  ')}`);
  process.exit(1);
}
console.log(`✓ no media in git (${files.length} tracked files checked)`);
