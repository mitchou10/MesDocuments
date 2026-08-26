<script setup lang="ts">
import { ref, watch } from 'vue'
import DocumentSources from '@/components/documents/DocumentSources.vue'
import type { DocumentSource } from '@/types'

const props = defineProps<{
  title: string
  showRecursiveOption?: boolean
  loading: boolean
  answer: string | null
  sources: DocumentSource[]
  fileNames?: Record<string, string>
  modal?: boolean
}>()

const emit = defineEmits<{ (e: 'ask', question: string, recursive: boolean): void }>()

const question = ref('')
const recursive = ref(true)
const modalOpened = ref(false)

function openModal() {
  modalOpened.value = true
}

function submit() {
  const trimmed = question.value.trim()
  if (!trimmed || props.loading) return
  emit('ask', trimmed, recursive.value)
}

watch(
  () => props.answer,
  (answer) => {
    if (props.modal && answer) question.value = ''
  },
)
</script>

<template>
  <div v-if="modal" class="flex flex-col gap-2">
    <button
      type="button"
      class="relative w-full rounded-full border border-[var(--border-default-grey)] bg-[var(--background-default-grey)] py-3 pl-11 pr-4 text-left text-sm text-[var(--text-mention-grey)] shadow-sm hover:bg-[var(--background-alt-grey)]"
      @click="openModal"
    >
      <span class="fr-icon-question-line absolute left-4 top-1/2 -translate-y-1/2" aria-hidden="true" />
      {{ title }}
    </button>

    <DsfrModal :opened="modalOpened" :title="title" size="md" :actions="[]" @update:opened="modalOpened = $event">
      <div class="flex flex-col gap-3">
        <form class="relative" @submit.prevent="submit">
          <input
            v-model="question"
            type="text"
            placeholder="Votre question…"
            :aria-label="title"
            autofocus
            class="w-full rounded-full border border-[var(--border-default-grey)] bg-[var(--background-default-grey)] py-3 pl-4 pr-12 text-sm focus:outline focus:outline-2 focus:outline-[var(--border-active-blue-france)]"
          />
          <button
            type="submit"
            class="absolute right-2 top-1/2 -translate-y-1/2 flex h-8 w-8 items-center justify-center rounded-full text-[var(--text-action-high-blue-france)] disabled:opacity-40"
            :class="loading ? 'fr-icon-refresh-line animate-spin' : 'fr-icon-arrow-right-line'"
            :disabled="loading || !question.trim()"
            aria-label="Demander"
          />
        </form>

        <label v-if="showRecursiveOption" class="flex items-center gap-1.5 self-end text-xs text-[var(--text-mention-grey)]">
          <input v-model="recursive" type="checkbox" class="h-3.5 w-3.5" />
          Inclure les sous-dossiers
        </label>

        <p v-if="loading" class="fr-text--sm text-[var(--text-mention-grey)] flex items-center gap-2">
          <span class="fr-icon-refresh-line animate-spin" aria-hidden="true" /> L'assistant analyse les documents…
        </p>

        <div v-else-if="answer" class="flex flex-col gap-3 border-t border-[var(--border-default-grey)] pt-3">
          <p class="fr-mb-0">{{ answer }}</p>
          <div v-if="sources.length">
            <p class="fr-text--sm font-medium fr-mb-1v">Sources</p>
            <DocumentSources :sources="sources" :file-names="fileNames" />
          </div>
        </div>
      </div>
    </DsfrModal>
  </div>

  <div v-else class="flex flex-col gap-2">
    <form class="relative" @submit.prevent="submit">
      <span
        class="fr-icon-question-line absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-mention-grey)]"
        aria-hidden="true"
      />
      <input
        v-model="question"
        type="text"
        :placeholder="title"
        :aria-label="title"
        class="w-full rounded-full border border-[var(--border-default-grey)] bg-[var(--background-default-grey)] py-3 pl-11 pr-12 text-sm shadow-sm focus:outline focus:outline-2 focus:outline-[var(--border-active-blue-france)]"
      />
      <button
        type="submit"
        class="absolute right-2 top-1/2 -translate-y-1/2 flex h-8 w-8 items-center justify-center rounded-full text-[var(--text-action-high-blue-france)] disabled:opacity-40"
        :class="loading ? 'fr-icon-refresh-line animate-spin' : 'fr-icon-arrow-right-line'"
        :disabled="loading || !question.trim()"
        aria-label="Demander"
      />
    </form>

    <label v-if="showRecursiveOption" class="flex items-center gap-1.5 self-end pr-3 text-xs text-[var(--text-mention-grey)]">
      <input v-model="recursive" type="checkbox" class="h-3.5 w-3.5" />
      Inclure les sous-dossiers
    </label>

    <div v-if="answer" class="fr-mt-1w flex flex-col gap-3 rounded-sm border border-[var(--border-default-grey)] p-4">
      <p class="fr-mb-0">{{ answer }}</p>
      <div v-if="sources.length">
        <p class="fr-text--sm font-medium fr-mb-1v">Sources</p>
        <DocumentSources :sources="sources" :file-names="fileNames" />
      </div>
    </div>
  </div>
</template>
