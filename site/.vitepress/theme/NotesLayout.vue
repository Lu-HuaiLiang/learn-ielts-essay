<script setup lang="ts">
import {computed} from 'vue';
import {useData} from 'vitepress';
import DefaultTheme from 'vitepress/theme';
import MubuPanel from './mubu/MubuPanel.vue';

const {page} = useData();
const essayId = computed(() => /^essays\/([a-z0-9-]+)\.md$/.exec(page.value.relativePath)?.[1]);
const vocabularyId = computed(() => /^vocabulary\/(chapter-\d{2})\.md$/.exec(page.value.relativePath)?.[1]);
const noteId = computed(() => essayId.value || (vocabularyId.value ? `vocabulary-${vocabularyId.value}` : undefined));
</script>

<template>
  <div :class="{'has-mubu': noteId}">
    <DefaultTheme.Layout />
    <ClientOnly>
      <MubuPanel v-if="noteId" :key="noteId" class="mubu-dock" :essay-id="noteId" :essay-title="page.title" />
    </ClientOnly>
  </div>
</template>
