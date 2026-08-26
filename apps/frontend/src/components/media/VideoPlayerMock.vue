<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'
import type { TranscriptSegment } from '@/types'
import { formatDuration } from '@/utils/format'

const props = defineProps<{
  title: string
  durationMs: number
  transcript: TranscriptSegment[]
  seekToMs?: number
}>()

const currentMs = ref(props.seekToMs ?? 0)
const playing = ref(false)
let timer: ReturnType<typeof setInterval> | null = null

watch(
  () => props.seekToMs,
  (value) => {
    if (value !== undefined) currentMs.value = value
  },
)

function togglePlay() {
  playing.value = !playing.value
  if (playing.value) {
    timer = setInterval(() => {
      currentMs.value = Math.min(currentMs.value + 1000, props.durationMs)
      if (currentMs.value >= props.durationMs) {
        playing.value = false
        if (timer) clearInterval(timer)
      }
    }, 1000)
  } else if (timer) {
    clearInterval(timer)
  }
}

function seekTo(ms: number) {
  currentMs.value = ms
}

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="aspect-video w-full bg-neutral-900 flex items-center justify-center rounded-sm">
      <span class="text-white/70 uppercase tracking-widest text-sm flex items-center gap-2">
        <span class="fr-icon-camera-line text-2xl" aria-hidden="true" /> Vidéo
      </span>
    </div>

    <p class="font-medium fr-mb-0">{{ title }}</p>

    <div class="flex items-center gap-3">
      <button
        type="button"
        class="fr-btn fr-btn--sm"
        :class="playing ? 'fr-icon-pause-circle-line' : 'fr-icon-play-line'"
        :aria-label="playing ? 'Mettre en pause' : 'Lire'"
        @click="togglePlay"
      />
      <input
        type="range"
        class="flex-1 accent-[var(--background-flat-blue-france)]"
        min="0"
        :max="durationMs"
        :value="currentMs"
        :aria-label="`Position de lecture, ${formatDuration(currentMs)} sur ${formatDuration(durationMs)}`"
        @input="seekTo(Number(($event.target as HTMLInputElement).value))"
      />
      <span class="fr-text--sm fr-mb-0 tabular-nums">{{ formatDuration(currentMs) }} / {{ formatDuration(durationMs) }}</span>
    </div>

    <div>
      <p class="fr-text--sm font-medium fr-mb-1w">Transcription</p>
      <ul class="flex flex-col gap-2 max-h-64 overflow-y-auto">
        <li v-for="(segment, index) in transcript" :key="index">
          <button
            type="button"
            class="w-full text-left rounded-sm px-2 py-1 hover:bg-[var(--background-alt-blue-france)]"
            :class="{ 'bg-[var(--background-alt-blue-france)]': currentMs >= segment.startMs && currentMs < segment.endMs }"
            @click="seekTo(segment.startMs)"
          >
            <span class="fr-text--xs text-[var(--text-mention-grey)] tabular-nums">{{ formatDuration(segment.startMs) }}</span>
            <span class="font-medium fr-ml-1w">{{ segment.speaker }}</span>
            <p class="fr-text--sm fr-mb-0">{{ segment.text }}</p>
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>
