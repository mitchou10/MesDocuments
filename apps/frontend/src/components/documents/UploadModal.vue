<script setup lang="ts">
import { ref, watch } from 'vue'
import { documentRepository } from '@/repositories'
import { formatBytes } from '@/utils/format'

type UploadStatus = 'selected' | 'uploading' | 'done' | 'error'

interface UploadItem {
  id: string
  name: string
  sizeBytes: number
  status: UploadStatus
  errorMessage?: string
}

const props = defineProps<{ opened: boolean; folderId: string | null }>()
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
  if (!props.folderId) return
  const folderId = props.folderId
  for (const file of Array.from(files)) {
    const item: UploadItem = {
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      name: file.name,
      sizeBytes: file.size,
      status: 'selected',
    }
    items.value.push(item)
    upload(item, folderId, file)
  }
}

async function upload(item: UploadItem, folderId: string, file: File) {
  item.status = 'uploading'
  try {
    await documentRepository.upload(folderId, file)
    item.status = 'done'
    emit('imported')
  } catch (error) {
    item.status = 'error'
    item.errorMessage = error instanceof Error ? error.message : "Erreur lors de l'import"
  }
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
      <button
        type="button"
        class="fr-btn fr-btn--secondary"
        :disabled="!folderId"
        @click="fileInput?.click()"
      >
        Choisir des fichiers
      </button>
      <label for="upload-modal-input" class="sr-only">Fichiers à importer</label>
      <input id="upload-modal-input" ref="fileInput" type="file" multiple class="sr-only" @change="onPick" />
      <p v-if="!folderId" class="fr-text--sm text-[var(--text-mention-grey)] fr-mt-2w fr-mb-0">
        Ouvrez un dossier avant d'importer des documents.
      </p>
    </div>

    <ul v-if="items.length" class="fr-mt-3w flex flex-col gap-3">
      <li v-for="item in items" :key="item.id" class="rounded-sm border border-[var(--border-default-grey)] p-3">
        <div class="flex items-center justify-between gap-3">
          <span class="truncate font-medium">{{ item.name }}</span>
          <span class="fr-text--sm text-[var(--text-mention-grey)] shrink-0">{{ formatBytes(item.sizeBytes) }}</span>
        </div>

        <p v-if="item.status === 'uploading'" class="fr-text--sm fr-mb-0 fr-mt-1w flex items-center gap-2">
          <span class="fr-icon-refresh-line animate-spin" aria-hidden="true" /> Envoi en cours…
        </p>

        <p v-else-if="item.status === 'done'" class="fr-text--sm fr-mb-0 fr-mt-1w text-[var(--text-default-success)] flex items-center gap-2">
          <span class="fr-icon-checkbox-circle-fill" aria-hidden="true" /> Upload terminé
        </p>

        <p v-else-if="item.status === 'error'" class="fr-text--sm fr-mb-0 fr-mt-1w text-[var(--text-default-error)] flex items-center gap-2">
          <span class="fr-icon-error-warning-fill" aria-hidden="true" /> {{ item.errorMessage ?? "Erreur lors de l'import" }}
        </p>
      </li>
    </ul>
  </DsfrModal>
</template>
