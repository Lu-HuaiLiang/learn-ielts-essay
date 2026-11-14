<script setup lang="ts">
import {computed, nextTick, onBeforeUnmount, onMounted, ref} from 'vue';
import {loadStoryProgress, saveStoryProgress} from './story-progress.mjs';

export type VocabularyStory = {
  title: string;
  groups: {id: string; title: string; start: number; end: number; count: number}[];
  steps: {id: string; word: string; meaning: string; before: string; after: string; groupId: string; groupTitle: string; groupStart: boolean; href: string}[];
};
const props = defineProps<{chapter: string; story: VocabularyStory}>();
const visible = ref(1);
const restored = ref(false);
let active = false;
const timeline = ref<HTMLOListElement>();
const card = ref<HTMLElement>();
const cardHeight = ref(0);
let layoutObserver: ResizeObserver | undefined;
const complete = computed(() => visible.value >= props.story.steps.length);
const shown = computed(() => props.story.steps.slice(0, visible.value));
const currentGroup = computed(() => props.story.groups.find(group => visible.value <= group.end) ?? props.story.groups[0]);

function saveProgress() {
  if (!restored.value) return;
  saveStoryProgress(props.chapter, props.story.steps[visible.value - 1].id, timeline.value?.scrollTop ?? 0);
}

async function moveTo(position: number) {
  if (!restored.value) return;
  visible.value = position;
  saveProgress();
  await nextTick();
  if (!active) return;
  if (timeline.value) timeline.value.scrollTop = position === 1 ? 0 : timeline.value.scrollHeight;
  saveProgress();
}

function jumpToGroup(event: Event) {
  const group = props.story.groups.find(group => group.id === (event.target as HTMLSelectElement).value);
  if (group) void moveTo(group.start + 1);
}

function advance() {
  if (!complete.value) void moveTo(visible.value + 1);
}

function resetProgress() {
  void moveTo(1);
}

function youdaoUrl(word: string) {
  const url = new URL('https://youdao.com/result');
  url.searchParams.set('word', word);
  url.searchParams.set('lang', 'en');
  return url.href;
}

const youdaoPopupName = 'vocabulary-youdao-dictionary';

function openWord(event: MouseEvent, word: string) {
  if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  saveProgress();
  event.preventDefault();
  window.open(youdaoUrl(word), youdaoPopupName, 'popup=yes,width=960,height=820');
}

function handleKeydown(event: KeyboardEvent) {
  if (!['ArrowDown', 'ArrowRight'].includes(event.key) || event.defaultPrevented ||
      event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || event.isComposing) return;
  const target = event.target instanceof Element ? event.target : null;
  if (target?.closest('input, textarea, select, [contenteditable]:not([contenteditable="false"]), [role="textbox"], [role="combobox"], [role="dialog"], .VPLocalSearchBox, .VPNav, .VPSidebar')) return;
  if (!restored.value) return;
  event.preventDefault();
  if (!event.repeat) advance();
}

function fitCardToViewport() {
  if (!active || !card.value) return;
  const top = card.value.getBoundingClientRect().top;
  cardHeight.value = Math.max(260, Math.floor(window.innerHeight - top - 100));
}

onMounted(async () => {
  active = true;
  window.addEventListener('keydown', handleKeydown);
  window.addEventListener('resize', fitCardToViewport);
  window.addEventListener('scroll', fitCardToViewport, {passive: true});
  layoutObserver = new ResizeObserver(fitCardToViewport);
  const picker = card.value?.previousElementSibling;
  if (picker) layoutObserver.observe(picker);
  const pageTitle = document.querySelector('.vocabulary-stories-page .vp-doc h1');
  if (pageTitle) layoutObserver.observe(pageTitle);
  await nextTick();
  fitCardToViewport();
  void document.fonts?.ready.then(fitCardToViewport);
  const saved = loadStoryProgress(props.chapter, props.story.steps);
  visible.value = saved.visible;
  await nextTick();
  if (!active) return;
  if (timeline.value) timeline.value.scrollTop = saved.scrollTop;
  restored.value = true;
});

onBeforeUnmount(() => {
  active = false;
  restored.value = false;
  window.removeEventListener('keydown', handleKeydown);
  window.removeEventListener('resize', fitCardToViewport);
  window.removeEventListener('scroll', fitCardToViewport);
  layoutObserver?.disconnect();
  layoutObserver = undefined;
});
</script>

<template>
  <section ref="card" class="vocabulary-story-card" :style="cardHeight ? {height: `${cardHeight}px`} : undefined" :data-story-chapter="chapter" :aria-labelledby="`story-title-${chapter}`">
    <header class="vocabulary-story-intro">
      <div class="vocabulary-story-heading">
        <p :id="`story-title-${chapter}`" class="vocabulary-story-title">{{ story.title }}</p>
        <p class="vocabulary-story-instruction">↓ / → 接下一个词 · 红色单词弹窗查看释义</p>
      </div>
      <button type="button" class="vocabulary-story-next" :disabled="!restored || complete" :aria-label="complete ? '故事已完成' : '接下一个词'" :title="complete ? '故事已完成' : '接下一个词（↓ / →）'" @click="advance">{{ complete ? '✓' : '👉' }}</button>
    </header>
    <div class="vocabulary-story-group-picker">
      <label :for="`vocabulary-story-group-${chapter}`">词群</label>
      <select :id="`vocabulary-story-group-${chapter}`" :value="currentGroup.id" :disabled="!restored" @change="jumpToGroup">
        <option v-for="(group, index) in story.groups" :key="group.id" :value="group.id">{{ index + 1 }} · {{ group.title }}（{{ group.count }}词）</option>
      </select>
      <button type="button" class="vocabulary-story-reset" :disabled="!restored" aria-label="重置本章故事" title="重置本章故事" @click="resetProgress">重置</button>
      <span class="vocabulary-story-coverage">全章 {{ story.steps.length }} 词</span>
    </div>
    <ol ref="timeline" class="vocabulary-story-steps" role="log" aria-label="已展开的单词故事" aria-live="polite" aria-relevant="additions" tabindex="0" @scroll="saveProgress">
      <li v-for="(step, index) in shown" :key="step.id" class="vocabulary-story-step" :data-story-word-id="step.id" :class="{'is-current': index === visible - 1}">
        <span class="vocabulary-story-number" aria-hidden="true">{{ index + 1 }}</span>
        <div class="vocabulary-story-message">
          <span class="vocabulary-story-speaker">{{ step.groupStart ? step.groupTitle : (index === visible - 1 ? '接到这里' : '故事接龙') }}</span>
          <p>{{ step.before }}<a class="vocabulary-story-word no-icon" :href="youdaoUrl(step.word)" target="_blank" rel="noopener noreferrer" :title="`在新窗口查看 ${step.word} 的有道释义`" lang="en" @click="openWord($event, step.word)">{{ step.word }}</a><span class="vocabulary-story-meaning">（{{ step.meaning }}）</span>{{ step.after }}</p>
        </div>
      </li>
    </ol>
    <footer class="vocabulary-story-controls">
      <span class="vocabulary-story-progress" role="status">{{ visible }} / {{ story.steps.length }} 个词</span>
      <span class="vocabulary-story-hint">{{ complete ? '故事完成 · 可重置本章' : '进度自动保存 · ↓ / → 继续' }}</span>
    </footer>
  </section>
</template>
