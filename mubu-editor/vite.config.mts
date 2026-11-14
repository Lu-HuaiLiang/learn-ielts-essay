import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';

export default defineConfig({
  root: fileURLToPath(new URL('.', import.meta.url)),
  base: './',
  esbuild: {jsx: 'automatic', jsxImportSource: 'react'},
  build: {outDir: fileURLToPath(new URL('../site/public/mubu', import.meta.url)), emptyOutDir: true},
});
