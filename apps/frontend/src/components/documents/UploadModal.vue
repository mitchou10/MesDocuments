<script setup lang="ts">
import { ref, watch } from 'vue'
import { formatBytes } from '@/utils/format'

type UploadStatus = 'selected' | 'uploading' | 'done' | 'error' | 'processing'

interface UploadItem {
  id: string
  name: string
  sizeBytes: number
  status: UploadStatus
  progress: number
  processingSteps: { label: string; done: boolean }[]
}

const props = defineProps<{ opened: boolean }>()
const emit = defineEmits<{ (e: 'update:opened', value: boolean): void; (e: 'imported'): void }>()

const items = ref<UploadItem[]>([])
const isDragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

watch(
  () => props.opened,
  (opened) => {
    if (opened) items.value = []
  },
)

function close() {
  emit('update:opened', false)
}

function onDrop(event: DragEvent) {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files) addFiles(files)
}

function onPick(event: Event) {
  const files = (event.target as HTMLInputElement).files
  if (files) addFiles(files)
}

function addFiles(files: FileList) {
  for (const file of Array.from(files)) {
    const item: UploadItem = {
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      name: file.name,
      sizeBytes: file.size,
      status: 'selected',
      progress: 0,
      processingSteps: [
        { label: 'Texte extrait', done: false },
        { label: 'Résumé généré', done: false },
        { label: 'Indexation terminée', done: false },
      ],
    }
    items.value.push(item)
    simulateUpload(item)
  }
}

function simulateUpload(item: UploadItem) {
  item.status = 'uploading'
  const interval = setInterval(() => {
    item.progress = Math.min(100, item.progress + 10 + Math.random() * 15)
    if (item.progress >= 100) {
      clearInterval(interval)
      item.status = 'processing'
      simulateProcessing(item)
    }
  }, 250)
}

function simulateProcessing(item: UploadItem) {
  let stepIndex = 0
  const interval = setInterval(() => {
    if (stepIndex < item.processingSteps.length) {
      item.processingSteps[stepIndex].done = true
      stepIndex += 1
    } else {
      clearInterval(interval)
      item.status = 'done'
      emit('imported')
    }
  }, 500)
}
</script>

<template>
  <DsfrModal
    :opened="opened"
    title="Importer des documents"
    size="lg"
    :actions="[{ label: 'Fermer', onClick: close }]"
    @update:opened="emit('update:opened', $event)"
  >
    <div
      class="rounded-sm border-2 border-dashed border-[var(--border-default-grey)] p-8 text-center"
      :class="{ 'border-[var(--border-active-blue-france)] bg-[var(--background-alt-blue-france)]': isDragging }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onDrop"
    >
      <p class="fr-mb-2w">Déposez vos fichiers ici</p>
      <p class="fr-text--sm text-[var(--text-mention-grey)] fr-mb-2w">ou</p>
      <button type="button" class="fr-btn fr-btn--secondary" @click="fileInput?.click()">Choisir des fichiers</button>
      <input ref="fileInput" type="file" multiple class="sr-only" @change="onPick" />
    </div>

    <ul v-if="items.length" class="fr-mt-3w flex flex-col gap-3">
      <li v-for="item in items" :key="item.id" class="rounded-sm border border-[var(--border-default-grey)] p-3">
        <div class="flex items-center justify-between gap-3">
          <span class="truncate font-medium">{{ item.name }}</span>
          <span class="fr-text--sm text-[var(--text-mention-grey)] shrink-0">{{ formatBytes(item.sizeBytes) }}</span>
        </div>

        <div v-if="item.status === 'uploading'" class="fr-mt-1w">
          <div class="h-1.5 rounded-full bg-[var(--background-alt-grey)] overflow-hidden">
            <div class="h-full bg-[var(--background-flat-blue-france)]" :style="{ width: `${item.progress}%` }" />
          </div>
          <p class="fr-text--xs fr-mb-0 fr-mt-1v">{{ Math.round(item.progress) }} %</p>
        </div>

        <div v-else-if="item.status === 'processing'" class="fr-mt-1w">
          <p class="fr-text--sm fr-mb-1v">Analyse du document</p>
          <ul class="flex flex-col gap-1">
            <li v-for="step in item.processingSteps" :key="step.label" class="fr-text--sm fr-mb-0 flex items-center gap-2">
              <span :class="step.done ? 'fr-icon-checkbox-circle-fill text-[var(--text-default-success)]' : 'fr-icon-refresh-line animate-spin'" aria-hidden="true" />
              {{ step.label }}
            </li>
          </ul>
        </div>

        <p v-else-if="item.status === 'done'" class="fr-text--sm fr-mb-0 fr-mt-1w text-[var(--text-default-success)] flex items-center gap-2">
          <span class="fr-icon-checkbox-circle-fill" aria-hidden="true" /> Upload terminé
        </p>

        <p v-else-if="item.status === 'error'" class="fr-text--sm fr-mb-0 fr-mt-1w text-[var(--text-default-error)] flex items-center gap-2">
          <span class="fr-icon-error-warning-fill" aria-hidden="true" /> Erreur lors de l'import
        </p>
      </li>
    </ul>
  </DsfrModal>
</template>
