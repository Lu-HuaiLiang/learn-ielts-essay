<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, ref} from 'vue';
import {withBase} from 'vitepress';

const props = defineProps<{essayId: string; essayTitle: string}>();
const frame = ref<HTMLIFrameElement>();
const status = ref('正在加载');
const source = computed(() => `${withBase('/mubu/index.html')}?essay=${encodeURIComponent(props.essayId)}`);
function receive(event: MessageEvent) {
  if (event.origin !== location.origin || event.source !== frame.value?.contentWindow) return;
  if (event.data?.type === 'mubu-status' && event.data.essayId === props.essayId && typeof event.data.text === 'string') status.value = event.data.text;
}
onMounted(() => window.addEventListener('message', receive));
onBeforeUnmount(() => window.removeEventListener('message', receive));
</script>

<template>
  <section class="mubu-panel" role="region" aria-label="幕布笔记">
    <iframe ref="frame" :src="source" title="幕布编辑器" class="mubu-frame" />
    <footer class="mubu-save-state" role="status">{{ status }}</footer>
  </section>
</template>
