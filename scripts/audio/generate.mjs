import {mkdir, rename, rm, stat} from 'node:fs/promises';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {checkAudioFiles, buildAudioManifest, loadEssays, root, audioRoot} from './essay-audio.mjs';

const checkOnly = process.argv.includes('--check');
const concurrency = Number(process.env.AUDIO_CONCURRENCY || 4);

function runSynthesis(item, output) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [path.join(root, 'scripts/audio/synthesize.mjs'), item.text, output], {stdio: 'inherit'});
    child.on('error', reject);
    child.on('exit', code => code === 0 ? resolve() : reject(new Error(`synthesis exited with ${code}`)));
  });
}

async function generateItem(item) {
  const output = path.join(root, 'site', 'public', item.path);
  await mkdir(path.dirname(output), {recursive: true});
  try {
    const info = await stat(output);
    if (info.isFile() && info.size >= 128) return;
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
  const temporary = `${output}.tmp-${process.pid}`;
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      await rm(temporary, {force: true});
      await runSynthesis(item, temporary);
      await rename(temporary, output);
      return;
    } catch (error) {
      await rm(temporary, {force: true});
      if (attempt === 3) throw new Error(`${item.path}: ${error.message}`);
      await new Promise(resolve => setTimeout(resolve, attempt * 1000));
    }
  }
}

const essays = await loadEssays();
const manifest = buildAudioManifest(essays);
if (checkOnly) {
  const result = await checkAudioFiles(essays);
  if (result.missing.length || result.invalid.length || result.unexpected.length) {
    console.error(`Audio check failed: ${result.missing.length} missing, ${result.invalid.length} invalid, ${result.unexpected.length} unexpected.`);
    for (const item of [...result.missing, ...result.invalid, ...result.unexpected]) console.error(`- ${item}`);
    process.exitCode = 1;
  } else {
    console.log(`PASS: ${result.manifest.length} Microsoft en-US-AriaNeural MP3 files present.`);
  }
} else {
  let cursor = 0;
  async function worker() {
    while (cursor < manifest.length) {
      const item = manifest[cursor++];
      console.log(`Generating ${cursor}/${manifest.length}: ${item.path}`);
      await generateItem(item);
    }
  }
  await Promise.all(Array.from({length: Math.max(1, concurrency)}, worker));
  const result = await checkAudioFiles(essays);
  if (result.missing.length || result.invalid.length || result.unexpected.length) throw new Error('Audio generation completed with an incomplete manifest.');
  console.log(`PASS: generated and checked ${result.manifest.length} MP3 files in ${audioRoot}.`);
}
