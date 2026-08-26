<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    page: number
    totalPages: number
    bbox?: [number, number, number, number]
  }>(),
  { totalPages: 1 },
)

const emit = defineEmits<{ (e: 'update:page', page: number): void }>()

const highlightStyle = computed(() => {
  if (!props.bbox) return null
  const [x0, y0, x1, y1] = props.bbox
  return {
    left: `${(x0 / 600) * 100}%`,
    top: `${(y0 / 800) * 100}%`,
    width: `${((x1 - x0) / 600) * 100}%`,
    height: `${((y1 - y0) / 800) * 100}%`,
  }
})

function goTo(page: number) {
  emit('update:page', Math.min(Math.max(page, 1), props.totalPages))
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <div class="flex items-center justify-between gap-2 flex-wrap">
      <div class="flex items-center gap-2">
        <button type="button" class="fr-btn fr-btn--tertiary fr-btn--sm fr-icon-arrow-left-s-line" aria-label="Page précédente" :disabled="page <= 1" @click="goTo(page - 1)" />
        <span class="fr-text--sm fr-mb-0">Page {{ page }} / {{ totalPages }}</span>
        <button type="button" class="fr-btn fr-btn--tertiary fr-btn--sm fr-icon-arrow-right-s-line" aria-label="Page suivante" :disabled="page >= totalPages" @click="goTo(page + 1)" />
      </div>
      <div class="flex items-center gap-2 text-sm text-[var(--text-mention-grey)]">
        <span class="fr-icon-zoom-out-line" aria-hidden="true" />
        100 %
        <span class="fr-icon-zoom-in-line" aria-hidden="true" />
      </div>
    </div>

    <div class="relative mx-auto w-full max-w-[420px] aspect-[3/4] bg-white border border-[var(--border-default-grey)] shadow-sm overflow-hidden">
      <div class="absolute inset-0 p-6 flex flex-col gap-2 text-[10px] leading-relaxed text-[var(--text-mention-grey)]">
        <div class="h-3 w-2/3 bg-[var(--background-alt-grey)] rounded" />
        <div v-for="i in 14" :key="i" class="h-2 bg-[var(--background-alt-grey)] rounded" :style="{ width: `${70 + ((i * 13) % 25)}%` }" />
      </div>
      <div
        v-if="highlightStyle"
        class="absolute rounded-sm bg-yellow-300/50 ring-2 ring-yellow-500"
        :style="highlightStyle"
        aria-hidden="true"
      />
    </div>
  </div>
</template>
