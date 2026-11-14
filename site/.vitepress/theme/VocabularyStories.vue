<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, ref} from 'vue';
import {withBase} from 'vitepress';
import VocabularyStoryChain, {type VocabularyStory} from './VocabularyStoryChain.vue';

const props = defineProps<{stories: (VocabularyStory & {id: string; topic: string})[]}>();
const selected = ref(props.stories[0].id);
const current = computed(() => props.stories.find(story => story.id === selected.value) ?? props.stories[0]);

function readLocation() {
  const id = /^#story-(\d{2})$/.exec(window.location.hash)?.[1];
  selected.value = props.stories.some(story => story.id === id) ? id! : props.stories[0].id;
}
function selectStory(event: Event) {
  selected.value = (event.target as HTMLSelectElement).value;
  window.history.pushState(window.history.state, '', `#story-${selected.value}`);
}
onMounted(() => {
  readLocation();
  window.addEventListener('hashchange', readLocation);
  window.addEventListener('popstate', readLocation);
  window.addEventListener('vocabulary-route-ready', readLocation);
});
onBeforeUnmount(() => {
  window.removeEventListener('hashchange', readLocation);
  window.removeEventListener('popstate', readLocation);
  window.removeEventListener('vocabulary-route-ready', readLocation);
});
</script>

<template>
  <div class="vocabulary-stories">
    <span v-for="story in stories" :id="`story-${story.id}`" :key="story.id" class="vocabulary-story-route" aria-hidden="true"></span>
    <div class="vocabulary-story-picker">
      <label for="vocabulary-story-topic">选择主题</label>
      <select id="vocabulary-story-topic" :value="selected" @change="selectStory">
        <option v-for="story in stories" :key="story.id" :value="story.id">{{ story.id }} · {{ story.topic }}（{{ story.steps.length }}词）</option>
      </select>
      <a :href="withBase(`/vocabulary/chapter-${current.id}.html`)">阅读本章词汇 →</a>
    </div>
    <VocabularyStoryChain :key="current.id" :chapter="current.id" :story="current" />
  </div>
</template>
