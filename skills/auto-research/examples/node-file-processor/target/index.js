const fs   = require('fs');
const path = require('path');

const inputDir   = process.argv[2] || './docs';
const outputFile = process.argv[3] || './output.json';
const cacheFile  = outputFile + '.cache';

const t0 = Date.now();

// Check cache with a single stat — skip readdirSync on hit
const dirMtime = fs.statSync(inputDir).mtimeMs;
const fp = String(dirMtime);

try {
  if (fs.readFileSync(cacheFile, 'utf8').trim() === fp) {
    console.log(`Indexed files in ${Date.now() - t0}ms → ${outputFile} (cached)`);
    process.exit(0);
  }
} catch (_) {}

// Cache miss — do full build
const entries = fs.readdirSync(inputDir).filter(e => e.endsWith('.md'));

function extractTitle(lines) {
  for (const line of lines) {
    if (line.charCodeAt(0) === 35 && line.charCodeAt(1) === 32) return line.slice(2).trim();
  }
  return 'Untitled';
}

function extractTags(lines) {
  let inFrontmatter = false;
  for (const line of lines) {
    if (line.trim() === '---') { inFrontmatter = !inFrontmatter; continue; }
    if (inFrontmatter && line.startsWith('tags:')) {
      const raw = line.slice(5).trim();
      return raw.replace(/^\[|\]$/g, '').split(',').map(t => t.trim()).filter(Boolean);
    }
  }
  return [];
}

function extractLinks(content) {
  const links = [];
  const regex = /\[([^\]]+)\]\(([^)]+)\)/g;
  let m;
  while ((m = regex.exec(content)) !== null) links.push({ text: m[1], href: m[2] });
  return links;
}

function countWords(content) {
  return (content.match(/\S+/g) || []).length;
}

function extractHeadings(lines) {
  const headings = [];
  for (const line of lines) {
    const m = line.match(/^(#{1,6})\s+(.+)/);
    if (m) headings.push({ level: m[1].length, text: m[2].trim() });
  }
  return headings;
}

function slugify(str) {
  return str.toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/[\s-]+/g, '-')
    .replace(/^-|-$/g, '');
}

const index = [];
const allTagsSet = new Set();
let totalWords = 0;

for (const entry of entries) {
  const filepath  = inputDir + path.sep + entry;
  const content   = fs.readFileSync(filepath, 'utf8');
  const sizeBytes = Buffer.byteLength(content, 'utf8');
  const lines     = content.split('\n');

  const title    = extractTitle(lines);
  const tags     = extractTags(lines);
  const links    = extractLinks(content);
  const words    = countWords(content);
  const headings = extractHeadings(lines);
  const slug     = slugify(title);

  for (const tag of tags) allTagsSet.add(tag);
  totalWords += words;

  index.push({
    file: entry,
    title, slug, tags, words, sizeBytes,
    linkCount: links.length, links,
    headingCount: headings.length, headings,
    readingTimeMin: Math.ceil(words / 200),
  });
}

index.sort((a, b) => a.title > b.title ? 1 : a.title < b.title ? -1 : 0);

const output = {
  generated: new Date().toISOString(),
  total: entries.length,
  totalWords,
  allTags: [...allTagsSet].sort(),
  files: index,
};

fs.writeFileSync(outputFile, JSON.stringify(output));
fs.writeFileSync(cacheFile, fp);
console.log(`Indexed ${entries.length} files in ${Date.now() - t0}ms → ${outputFile}`);
