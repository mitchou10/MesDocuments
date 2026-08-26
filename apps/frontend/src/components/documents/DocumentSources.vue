<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { DocumentSource } from '@/types'
import { formatDuration } from '@/utils/format'

const props = defineProps<{ sources: DocumentSource[]; fileNames?: Record<string, string> }>()
const router = useRouter()

function label(source: DocumentSource): string {
  const name = props.fileNames?.[source.fileId] ?? source.fileId
  if (source.type === 'pdf') return `${name} — page ${source.page}`
  return `${name} — ${formatDuration(source.startMs)} → ${formatDuration(source.endMs)}`
}

function openSource(source: DocumentSource) {
  const query: Record<string, string> =
    source.type === 'pdf'
      ? { page: String(source.page), ...(source.bbox ? { bbox: source.bbox.join(',') } : {}) }
      : { startMs: String(source.startMs), endMs: String(source.endMs) }
  router.push({ name: 'file', params: { fileId: source.fileId }, query })
}
</script>

<template>
  <ul class="flex flex-col gap-2">
    <li
      v-for="(source, index) in sources"
      :key="`${source.fileId}-${index}`"
      class="flex items-center justify-between gap-3 rounded-sm border border-[var(--border-default-grey)] px-3 py-2"
    >
      <span class="flex items-center gap-2 text-sm">
        <span :class="source.type === 'pdf' ? 'fr-icon-file-pdf-line' : source.type === 'audio' ? 'fr-icon-mic-line' : 'fr-icon-camera-line'" aria-hidden="true" />
        {{ label(source) }}
      </span>
      <button type="button" class="fr-btn fr-btn--tertiary fr-btn--sm" @click="openSource(source)">Voir la source</button>
    </li>
  </ul>
</template>
