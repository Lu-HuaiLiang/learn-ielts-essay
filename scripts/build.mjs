import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
let html = await readFile(path.join(root, 'index.html'), 'utf8');
const css = await readFile(path.join(root, 'style.css'), 'utf8');
html = html.replace('<link rel="stylesheet" href="style.css">', `<style>${css}</style>`);
const scripts = [];
for (const file of ['course-model.js','course-data.js','app.js']) {
  const code = await readFile(path.join(root, file), 'utf8');
  html = html.replace(`  <script defer src="${file}"></script>\n`, '');
  scripts.push(`<script>\n${code.replace(/<\/script/gi, '<\\/script')}\n</script>`);
}
html = html.replace('</body>', `${scripts.join('\n')}\n</body>`);
await mkdir(path.join(root, 'dist'), {recursive:true});
await writeFile(path.join(root, 'dist/index.html'), html);
console.log(`Built dist/index.html (${Math.round(Buffer.byteLength(html)/1024)} KB), with all styles, data and scripts embedded.`);
