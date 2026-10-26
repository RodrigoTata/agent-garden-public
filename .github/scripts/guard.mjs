#!/usr/bin/env node
// Generic leak guard: secrets, personal emails, workstation paths, unexpected binaries,
// and SKILL.md license metadata. Contains no private names (those live in the private repo).
// Usage: node .github/scripts/guard.mjs [dir]
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative, extname, sep, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const allow = JSON.parse(readFileSync(join(here, 'guard-allow.json'), 'utf8'));

const EMAIL = /[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z]{2,})+\b/g;
const RULES = [
  ['workstation path', /[A-Za-z]:[\\/]+(?:Users[\\/](?!\$env|\.\.\.|<|%|\{)|dev[\\/])/i],
  ['unix home path', /\/(?:Users|home)\/[a-z][\w.-]+\//],
  ['AWS key', /AKIA[0-9A-Z]{16}/],
  ['Google API key', /AIza[0-9A-Za-z_-]{35}/],
  ['GitHub token', /\b(?:ghp|gho|ghs|ghu)_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}/],
  ['Slack token', /xox[abprs]-[A-Za-z0-9-]{10,}/],
  ['Anthropic/OpenAI key', /\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}/],
  ['Notion token', /\b(?:ntn|secret)_[A-Za-z0-9]{30,}/],
  ['private key', /-----BEGIN [A-Z ]*PRIVATE KEY-----/],
  ['hardcoded credential', /\b(?:password|passwd|secret|api[_-]?key|token)\b\s*[:=]\s*['"][^'"\s$<{]{12,}['"]/i],
];

export function* walk(root) {
  for (const e of readdirSync(root, { withFileTypes: true })) {
    if (e.name === '.git') continue;
    const p = join(root, e.name);
    if (e.isDirectory()) yield* walk(p);
    else if (e.isFile()) yield p;
  }
}

const isBinary = (buf) => buf.subarray(0, 8000).includes(0);

export function scanTree(root, extraRules = []) {
  const hits = [];
  const add = (file, rule, detail) => hits.push({ file, rule, detail });
  for (const abs of walk(root)) {
    const rel = relative(root, abs).split(sep).join('/');
    if (rel === '.github/scripts/guard-allow.json') continue;
    const size = statSync(abs).size;
    if (size > allow.maxFileBytes) add(rel, 'file too large', `${size} bytes`);
    const buf = readFileSync(abs);
    if (isBinary(buf)) {
      if (!allow.allowedBinaryExt.includes(extname(rel).toLowerCase())) add(rel, 'unexpected binary', extname(rel));
      continue;
    }
    const text = buf.toString('utf8');
    for (const [name, re] of [...RULES, ...extraRules]) {
      const g = new RegExp(re.source, re.flags.replace('g', '') + 'g');
      for (const m of text.matchAll(g)) {
        const ctx = text.slice(Math.max(0, m.index - 40), m.index + m[0].length + 40);
        if (allow.contains.some((a) => a.file === rel && ctx.includes(a.text))) continue;
        add(rel, name, m[0].slice(0, 60));
      }
    }
    for (const m of text.matchAll(EMAIL)) {
      if (allow.emails.some((p) => new RegExp(p, 'i').test(m[0]))) continue;
      add(rel, 'email', m[0]);
    }
    if (/(^|\/)SKILL\.md$/.test(rel)) {
      const fm = text.replace(/\r\n/g, '\n').match(/^---\n([\s\S]*?)\n---/);
      if (!fm) add(rel, 'skill frontmatter', 'missing');
      else if (!/^license:\s*\S+/m.test(fm[1])) add(rel, 'skill frontmatter', 'missing license');
    }
  }
  for (const f of ['LICENSE', 'NOTICE', 'README.md']) {
    try { statSync(join(root, f)); } catch { add(f, 'required file', 'missing'); }
  }
  return hits;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const root = process.argv[2] || '.';
  const hits = scanTree(root);
  for (const h of hits) console.error(`GUARD ${h.rule}: ${h.file}  ${h.detail}`);
  console.error(hits.length ? `\n${hits.length} finding(s). Blocked.` : 'guard: clean');
  process.exit(hits.length ? 1 : 0);
}
