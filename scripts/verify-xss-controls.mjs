import assert from 'node:assert/strict';
import { readdir, readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { safeMarkdownUrl } from '../src/security/safeMarkdown.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const sourceRoot = path.join(root, 'src');

assert.equal(safeMarkdownUrl('javascript:alert(1)', 'href'), '');
assert.equal(safeMarkdownUrl('JaVaScRiPt:alert(1)', 'href'), '');
assert.equal(safeMarkdownUrl('data:text/html,<script>alert(1)</script>', 'href'), '');
assert.equal(safeMarkdownUrl('data:image/svg+xml,<svg onload=alert(1)>', 'src'), '');
assert.equal(safeMarkdownUrl('vbscript:msgbox(1)', 'href'), '');
assert.equal(safeMarkdownUrl('https://example.edu/course', 'href'), 'https://example.edu/course');
assert.equal(safeMarkdownUrl('mailto:security@example.edu', 'href'), 'mailto:security@example.edu');
assert.equal(safeMarkdownUrl('/api/v1/local-storage/file', 'src'), '/api/v1/local-storage/file');
assert.equal(safeMarkdownUrl('media/diagram.png', 'src'), 'media/diagram.png');

async function sourceFiles(directory) {
  const entries = await readdir(directory);
  const files = [];
  for (const entry of entries) {
    const fullPath = path.join(directory, entry);
    const details = await stat(fullPath);
    if (details.isDirectory()) files.push(...await sourceFiles(fullPath));
    if (details.isFile() && /\.(js|jsx|mjs|ts|tsx)$/.test(entry)) files.push(fullPath);
  }
  return files;
}

for (const file of await sourceFiles(sourceRoot)) {
  const source = await readFile(file, 'utf8');
  assert.equal(
    source.includes('dangerouslySetInnerHTML'),
    false,
    `${path.relative(root, file)} introduces dangerouslySetInnerHTML`,
  );
}

const appEntry = await readFile(path.join(sourceRoot, 'pages', 'AppEntry.jsx'), 'utf8');
assert.equal(
  appEntry.includes('searchParams.get("session_token")'),
  false,
  'LTI session tokens must not be accepted from browser URLs',
);
assert.equal(
  appEntry.includes('searchParams.get("login_code")'),
  true,
  'LTI launch must use a short-lived one-time login code',
);

console.log('XSS controls verified: unsafe Markdown URLs blocked and no React HTML injection sinks found.');
