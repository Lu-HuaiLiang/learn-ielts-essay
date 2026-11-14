import {writeFile} from 'node:fs/promises';
import {EdgeTTS} from 'edge-tts-universal';

const [, , text, output] = process.argv;
if (!text || !output) throw new Error('Usage: node synthesize.mjs <text> <output>');

const tts = new EdgeTTS(text, 'en-US-AriaNeural');
const {audio} = await tts.synthesize();
if (audio.size === 0) throw new Error('Empty audio');
await writeFile(output, Buffer.from(await audio.arrayBuffer()));
