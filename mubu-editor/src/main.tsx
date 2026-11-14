import {createRoot} from 'react-dom/client';
import type {Node as PMNode} from 'prosemirror-model';
import App from './App';
import {schema, documentFrom, item} from './editor/model';
import './styles.css';
import './fonts.css';
import './embed.css';

const essayId = new URLSearchParams(location.search).get('essay') || 'unknown';
const storageKey = `ielts-essay.mubu.v1.${essayId}`;
let doc = documentFrom('', [item()]);
let lastSnapshot = '';
const status = (text: string) => parent.postMessage({type: 'mubu-status', essayId, text}, location.origin);
try {
  const raw = localStorage.getItem(storageKey);
  if (raw) {
    const saved = JSON.parse(raw);
    if (saved.version !== 1) throw new Error('Unknown note version');
    const restored = schema.nodeFromJSON(saved.doc);
    restored.check();
    if (restored.type !== schema.topNodeType) throw new Error('Invalid note document');
    doc = restored;
  }
  status(raw ? '已保存到本机' : '自动保存到本机');
} catch { status('未能读取本地笔记'); }
lastSnapshot = JSON.stringify({version: 1, doc: doc.toJSON()});
function save(doc: PMNode) {
  const snapshot = JSON.stringify({version: 1, doc: doc.toJSON()});
  if (snapshot === lastSnapshot) return;
  try {
    localStorage.setItem(storageKey, snapshot);
    lastSnapshot = snapshot;
    status('已保存到本机');
  } catch { status('未能保存，请保留此页面'); }
}
createRoot(document.getElementById('root')!).render(<App initialDocument={doc} onDocumentChange={save} />);
