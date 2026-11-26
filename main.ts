// News front page for Wednesday 25 November 2026 (news-image-20261125 v3b).
//
// This program builds the entry image from scratch when it can: it drives
// the Python renderer (draw_frontpage.py, same directory) and then checks
// the result the way the competition gate does — one PNG, at most 1024 by
// 1024 pixels and at most 1 MiB. The grader's image may not have Python or
// Pillow at all, so when the renderer cannot run, or its output fails the
// checks, the program falls back to the pre-rendered entry.png committed
// beside it (drawn by the same renderer in this session) and validates that
// instead. Either way it only ever writes a checked PNG.
//
// Run locally with:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
// The grader runs it with /output as the destination instead.

import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const RENDERER = join(HERE, 'draw_frontpage.py');
const PRE_RENDERED = join(HERE, 'entry.png');
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
    throw new Error('entry.png is not a PNG file');
  }
  if (buffer.toString('ascii', 12, 16) !== 'IHDR') {
    throw new Error('entry.png has no IHDR chunk where one belongs');
  }
  return {
    width: buffer.readUInt32BE(16),
    height: buffer.readUInt32BE(20),
  };
}

function checkTarget(): { width: number; height: number; bytes: Buffer } {
  if (!existsSync(TARGET)) throw new Error(`no image at ${TARGET}`);
  const bytes = readFileSync(TARGET);
  const { width, height } = pngSize(bytes);
  if (width > MAX_EDGE || height > MAX_EDGE) {
    throw new Error(`image is ${width}x${height}, over the ${MAX_EDGE}px edge limit`);
  }
  if (bytes.length > MAX_BYTES) {
    throw new Error(`image is ${bytes.length} bytes, over the 1 MiB limit`);
  }
  return { width, height, bytes };
}

function main(): void {
  mkdirSync(OUT_DIR, { recursive: true });
  let method = '';
  if (existsSync(RENDERER)) {
    const run = spawnSync('python3', [RENDERER, OUT_DIR], {
      cwd: HERE,
      encoding: 'utf8',
    });
    if (run.stdout) process.stdout.write(run.stdout);
    if (run.stderr) process.stderr.write(run.stderr);
    if (run.error) {
      console.error(`[frontpage] python3 unavailable (${run.error.message}), falling back`);
    } else if (run.status !== 0) {
      console.error(`[frontpage] renderer exited with status ${run.status}, falling back`);
    } else {
      try {
        checkTarget();
        method = 'rendered';
      } catch (error) {
        console.error(`[frontpage] rendered image failed validation (${(error as Error).message}), falling back`);
      }
    }
  } else {
    console.error('[frontpage] renderer missing, falling back');
  }
  if (!method) {
    if (!existsSync(PRE_RENDERED)) {
      fail('no renderer output and no pre-rendered entry.png to fall back to');
    }
    copyFileSync(PRE_RENDERED, TARGET);
    try {
      checkTarget();
    } catch (error) {
      fail(`pre-rendered image failed validation: ${(error as Error).message}`);
    }
    method = 'pre-rendered';
  }
  const { width, height, bytes } = checkTarget();
  const digest = createHash('sha256').update(bytes).digest('hex');
  const stats = statSync(TARGET);
  console.log(
    JSON.stringify(
      {
        program: 'news-image-20261125-v3b',
        date: '2026-11-25',
        method,
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
