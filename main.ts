// News front page for Wednesday 25 November 2026 (news-image-20261125 v3b).
//
// This program builds the entry image from scratch every run: it drives the
// Python renderer (draw_frontpage.py, same directory) and then checks the
// result the way the competition gate does — one PNG, at most 1024 by 1024
// pixels and at most 1 MiB — before declaring success. Nothing is copied
// from an earlier entry: the picture is drawn fresh from the story list
// baked into the renderer.
//
// Run locally with:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
// The grader runs it with /output as the destination instead.

import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const RENDERER = join(HERE, 'draw_frontpage.py');
const TARGET = join(OUT_DIR, 'entry.png');

const MAX_BYTES = 1024 * 1024;
const MAX_EDGE = 1024;

function fail(message: string): never {
  console.error(`[frontpage] FAIL: ${message}`);
  process.exit(1);
}

function pngSize(buffer: Buffer): { width: number; height: number } {
  const magic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  if (buffer.length < 24 || !buffer.subarray(0, 8).equals(magic)) {
    fail('entry.png is not a PNG file');
  }
  if (buffer.toString('ascii', 12, 16) !== 'IHDR') {
    fail('entry.png has no IHDR chunk where one belongs');
  }
  return {
    width: buffer.readUInt32BE(16),
    height: buffer.readUInt32BE(20),
  };
}

function main(): void {
  mkdirSync(OUT_DIR, { recursive: true });
  if (!existsSync(RENDERER)) fail(`renderer missing: ${RENDERER}`);

  const run = spawnSync('python3', [RENDERER, OUT_DIR], {
    cwd: HERE,
    encoding: 'utf8',
  });
  if (run.error) fail(`could not start python3: ${run.error.message}`);
  if (run.stdout) process.stdout.write(run.stdout);
  if (run.stderr) process.stderr.write(run.stderr);
  if (run.status !== 0) fail(`renderer exited with status ${run.status}`);

  if (!existsSync(TARGET)) fail(`renderer wrote no ${TARGET}`);
  const bytes = readFileSync(TARGET);
  const { width, height } = pngSize(bytes);
  if (width > MAX_EDGE || height > MAX_EDGE) {
    fail(`image is ${width}x${height}, over the ${MAX_EDGE}px edge limit`);
  }
  if (bytes.length > MAX_BYTES) {
    fail(`image is ${bytes.length} bytes, over the 1 MiB limit`);
  }
  const digest = createHash('sha256').update(bytes).digest('hex');
  const stats = statSync(TARGET);
  console.log(
    JSON.stringify(
      {
        program: 'news-image-20261125-v3b',
        date: '2026-11-25',
        stories: 36,
        regions: 8,
        illustrated: 13,
        alsoOn: 23,
        output: TARGET,
        width,
        height,
        bytes: stats.size,
        sha256: digest,
      },
      null,
      2,
    ),
  );
}

main();
