import {readFile, readdir, stat} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

export const root = path.resolve(fileURLToPath(new URL('../..', import.meta.url)));
export const audioRoot = path.join(root, 'site', 'public', 'audio', 'essays');

export function cleanParagraph(text) {
  return String(text).replaceAll('**', '').replace(/\s+/g, ' ').trim();
}

export function audioFileName(paragraphIndex) {
  return `p${String(paragraphIndex + 1).padStart(2, '0')}.mp3`;
}

export function buildAudioManifest(essays) {
  return essays.flatMap(essay => essay.paragraphs.map((text, paragraphIndex) => ({
    essayId: essay.id,
    paragraphIndex,
    text: cleanParagraph(text),
    path: `audio/essays/${essay.id}/${audioFileName(paragraphIndex)}`,
  })));
}

export async function loadEssays() {
  return JSON.parse(await readFile(path.join(root, 'data', 'essays.json'), 'utf8'));
}

export async function checkAudioFiles(essays) {
  essays ??= await loadEssays();
  const manifest = buildAudioManifest(essays);
  const missing = [];
  const invalid = [];
  for (const item of manifest) {
    const file = path.join(root, 'site', 'public', item.path);
    try {
      const info = await stat(file);
      if (!info.isFile() || info.size < 128) invalid.push(item.path);
    } catch (error) {
      if (error.code === 'ENOENT') missing.push(item.path);
      else throw error;
    }
  }
  const unexpected = [];
  const essayDirs = await readdir(audioRoot, {withFileTypes: true}).catch(error => {
    if (error.code === 'ENOENT') return [];
    throw error;
  });
  const expectedByEssay = new Map();
  for (const item of manifest) {
    const files = expectedByEssay.get(item.essayId) ?? new Set();
    files.add(audioFileName(item.paragraphIndex));
    expectedByEssay.set(item.essayId, files);
  }
  for (const entry of essayDirs) {
    if (!entry.isDirectory()) continue;
    const files = await readdir(path.join(audioRoot, entry.name), {withFileTypes: true});
    const expected = expectedByEssay.get(entry.name) ?? new Set();
    for (const file of files) {
      if (file.isFile() && file.name.endsWith('.mp3') && !expected.has(file.name)) {
        unexpected.push(`audio/essays/${entry.name}/${file.name}`);
      }
    }
  }
  return {manifest, missing, invalid, unexpected};
}
