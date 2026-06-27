const { workerData, parentPort } = require('worker_threads');
const fs   = require('fs');
const path = require('path');

const inputDir = workerData.inputDir;
const entries  = workerData.entries;

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

const results = [];
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

  results.push({ entry, title, slug, tags, words, sizeBytes, links, headings });
}
parentPort.postMessage(results);
