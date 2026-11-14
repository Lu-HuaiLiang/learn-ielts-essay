import assert from 'node:assert/strict';
import test from 'node:test';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {buildAudioManifest, audioFileName} from '../scripts/audio/essay-audio.mjs';
import {createEssayAudioController} from '../site/.vitepress/theme/essay-audio.mjs';

const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));

test('audio manifest covers every essay paragraph with stable names', async () => {
  const essays = JSON.parse(await readFile(path.join(root, 'data/essays.json'), 'utf8'));
  const manifest = buildAudioManifest(essays);
  assert.equal(manifest.length, 317);
  assert.equal(new Set(manifest.map(item => item.path)).size, 317);
  assert.equal(audioFileName(0), 'p01.mp3');
  assert.equal(audioFileName(8), 'p09.mp3');
  assert.equal(audioFileName(9), 'p10.mp3');
  assert.equal(manifest.at(-1).path, 'audio/essays/five-r3/p04.mp3');
});

class FakeAudio {
  static instances = [];
  src = '';
  onplaying = null;
  onended = null;
  onerror = null;
  paused = true;
  playCalls = 0;
  pauseCalls = 0;
  constructor() { FakeAudio.instances.push(this); }
  play() { this.playCalls += 1; this.paused = false; return Promise.resolve(); }
  pause() { this.pauseCalls += 1; this.paused = true; }
  load() {}
  emit(name, value) { this[name]?.(value); }
}

function controllerWith(states) {
  FakeAudio.instances = [];
  return createEssayAudioController({
    createAudio: () => new FakeAudio(),
    urlForParagraph: index => `/audio/p${index + 1}.mp3`,
    onStateChange: state => states.push({...state}),
  });
}

test('audio controller plays, stops, switches, and reuses one audio element', async () => {
  const states = [];
  const controller = controllerWith(states);
  controller.toggle(0);
  const audio = FakeAudio.instances.at(-1);
  assert.equal(audio.src, '/audio/p1.mp3');
  assert.deepEqual(controller.getState(), {status: 'loading', activeParagraph: 0, failedParagraph: null});
  audio.emit('onplaying');
  assert.equal(controller.getState().status, 'playing');
  controller.toggle(1);
  assert.equal(FakeAudio.instances.length, 1);
  assert.equal(audio.src, '/audio/p2.mp3');
  assert.equal(audio.pauseCalls, 1);
  controller.toggle(1);
  assert.equal(controller.getState().status, 'idle');
  assert.ok(states.some(state => state.status === 'playing'));
});

test('stale callbacks cannot change the state after switching paragraphs', () => {
  const states = [];
  const controller = controllerWith(states);
  controller.toggle(0);
  const audio = FakeAudio.instances.at(-1);
  const oldPlaying = audio.onplaying;
  const oldEnded = audio.onended;
  controller.toggle(1);
  oldPlaying?.();
  oldEnded?.();
  assert.deepEqual(controller.getState(), {status: 'loading', activeParagraph: 1, failedParagraph: null});
});

test('natural completion returns to idle and load errors remain retryable', () => {
  const states = [];
  const controller = controllerWith(states);
  controller.toggle(0);
  const audio = FakeAudio.instances.at(-1);
  audio.emit('onplaying');
  audio.emit('onended');
  assert.deepEqual(controller.getState(), {status: 'idle', activeParagraph: null, failedParagraph: null});
  controller.toggle(0);
  audio.emit('onerror', new Error('network'));
  assert.deepEqual(controller.getState(), {status: 'error', activeParagraph: 0, failedParagraph: 0});
  controller.toggle(0);
  assert.equal(controller.getState().status, 'loading');
  assert.equal(audio.playCalls, 3);
});
