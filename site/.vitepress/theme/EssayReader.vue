<script setup lang="ts">
import {onBeforeUnmount, ref, watch} from 'vue';
import {useRoute, withBase} from 'vitepress';
import {createEssayAudioController} from './essay-audio.mjs';

type ReadingMode = 'original' | 'structured' | 'translated';
const props = defineProps<{essayId: string; paragraphs: string[]}>();
const mode = ref<ReadingMode>('original');
const route = useRoute();
const expanded = ref(true);
const activeParagraph = ref<number | null>(null);
const speechError = ref('');
const playbackStatus = ref<'idle' | 'loading' | 'playing' | 'error'>('idle');
const failedParagraph = ref<number | null>(null);
const audioController = createEssayAudioController({
  createAudio: () => new Audio(),
  urlForParagraph: index => withBase(`/audio/essays/${props.essayId}/p${String(index + 1).padStart(2, '0')}.mp3`),
  onStateChange: state => {
    playbackStatus.value = state.status;
    activeParagraph.value = state.activeParagraph;
    failedParagraph.value = state.failedParagraph;
    speechError.value = state.status === 'error' ? '美音加载失败，请重试。' : '';
  },
});

function stopReading() {
  audioController.stop();
}

function readParagraph(index: number) {
  audioController.toggle(index);
}

function selectMode(selected: ReadingMode) {
  mode.value = mode.value === selected ? 'original' : selected;
}
watch(() => route.path, () => {
  stopReading();
  mode.value = 'original';
});
function toggled(event: Event) {
  expanded.value = (event.target as HTMLDetailsElement).open;
  if (!expanded.value) stopReading();
}
onBeforeUnmount(stopReading);
</script>

<template>
  <details class="custom-block details essay-block essay-reader" open @toggle="toggled">
    <summary>
      <h2 id="essay" class="essay-section-title">范文</h2>
      <span v-show="expanded" class="essay-view-controls">
        <button
          type="button"
          class="essay-view-toggle"
          :aria-pressed="mode === 'structured'"
          aria-controls="essay-reading"
          @click.stop.prevent="selectMode('structured')"
        >结构化阅读</button>
        <button
          type="button"
          class="essay-view-toggle"
          :aria-pressed="mode === 'translated'"
          aria-controls="essay-reading"
          @click.stop.prevent="selectMode('translated')"
        >全文翻译</button>
        <span class="essay-speech-controls" role="group" aria-label="分段朗读">
          <button
            v-for="(_, index) in paragraphs"
            :key="index"
            type="button"
            class="essay-view-toggle essay-read-aloud"
            :class="{'is-loading': playbackStatus === 'loading' && activeParagraph === index}"
            :aria-label="failedParagraph === index ? `重试朗读第${index + 1}段` : activeParagraph === index ? `停止朗读第${index + 1}段` : `朗读第${index + 1}段`"
            :aria-pressed="activeParagraph === index"
            :aria-busy="playbackStatus === 'loading' && activeParagraph === index"
            @click.stop.prevent="readParagraph(index)"
          >{{ index + 1 }}</button>
        </span>
      </span>
    </summary>
    <div id="essay-reading">
      <p v-if="speechError" class="essay-speech-error" role="status">{{ speechError }}</p>
      <p class="essay-learning-guide">紫色加粗标出引题、理由、让步反驳、举例与结论等文章框架表达；红色加粗为本篇精选词汇与表达，可在下方「词汇与短语积累」查看用法和例句。</p>
      <slot v-if="mode === 'original'" name="original" />
      <slot v-else-if="mode === 'structured'" name="structured" />
      <slot v-else name="translated" />
    </div>
  </details>
</template>
