<script setup lang="ts">
import {nextTick, onBeforeUnmount, onMounted, ref} from 'vue';
import {getScrollOffset} from 'vitepress';

const root = ref<HTMLElement>();
const markPrefix = 'ielts-vocabulary.mark.v1.';
const markCache = new Map<string, boolean>();

function readMark(id: string) {
  try {
    const green = window.localStorage.getItem(markPrefix + id) === 'green';
    markCache.set(id, green);
    return green;
  } catch {
    return markCache.get(id) ?? false;
  }
}

function paintMark(button: HTMLButtonElement, green: boolean) {
  const label = `${button.dataset.markLabel}：${green ? '绿色' : '红色'}，点击切换为${green ? '红色' : '绿色'}`;
  button.textContent = green ? '🟢' : '🔴';
  button.setAttribute('aria-pressed', String(green));
  button.setAttribute('aria-label', label);
  button.title = label;
}

function restoreMarks() {
  root.value?.querySelectorAll<HTMLButtonElement>('.vocabulary-word-mark').forEach(button => {
    if (button.dataset.markWord) paintMark(button, readMark(button.dataset.markWord));
  });
}

function toggleMark(event: MouseEvent) {
  const button = event.target instanceof Element
    ? event.target.closest<HTMLButtonElement>('.vocabulary-word-mark') : null;
  const id = button?.dataset.markWord;
  if (!button || !id || !root.value?.contains(button)) return;
  event.preventDefault();
  event.stopPropagation();
  const green = button.getAttribute('aria-pressed') !== 'true';
  markCache.set(id, green);
  paintMark(button, green);
  try {
    if (green) window.localStorage.setItem(markPrefix + id, 'green');
    else window.localStorage.removeItem(markPrefix + id);
  } catch { /* Keep the toggle usable when browser storage is unavailable. */ }
}

function syncMarks(event: StorageEvent) {
  if (event.key === null || event.key.startsWith(markPrefix)) restoreMarks();
}

async function revealWord() {
  let id: string;
  try { id = decodeURIComponent(window.location.hash.slice(1)); } catch { return; }
  if (!id.startsWith('word-')) return;
  await nextTick();
  const target = document.getElementById(id);
  if (!target || !root.value?.contains(target)) return;
  const panel = target.closest<HTMLDetailsElement>('details.vocabulary-word');
  if (panel) {
    panel.open = true;
    requestAnimationFrame(() => {
      if (target.isConnected) window.scrollTo(0, window.scrollY + target.getBoundingClientRect().top - getScrollOffset());
    });
  }
}
async function refreshReader() {
  await nextTick();
  restoreMarks();
  await revealWord();
}

onMounted(() => {
  refreshReader();
  window.addEventListener('hashchange', revealWord);
  window.addEventListener('vocabulary-route-ready', refreshReader);
  window.addEventListener('storage', syncMarks);
});
onBeforeUnmount(() => {
  window.removeEventListener('hashchange', revealWord);
  window.removeEventListener('vocabulary-route-ready', refreshReader);
  window.removeEventListener('storage', syncMarks);
});
</script>

<template>
  <div ref="root" class="vocabulary-reader" @click="toggleMark"><slot /></div>
</template>
