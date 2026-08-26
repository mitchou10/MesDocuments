<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LoadingState from '@/components/common/LoadingState.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import FolderBreadcrumb from '@/components/folders/FolderBreadcrumb.vue'
import FileFolderTable from '@/components/documents/FileFolderTable.vue'
import NewFolderModal from '@/components/folders/NewFolderModal.vue'
import UploadModal from '@/components/documents/UploadModal.vue'
import QuestionBox from '@/components/agent/QuestionBox.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { documentRepository, folderRepository } from '@/repositories'
import type { DocumentFile, DocumentSource, Folder } from '@/types'

const route = useRoute()
const router = useRouter()

const folderId = computed<string | null>(() => (route.params.folderId as string | undefined) ?? null)
const sortBy = ref<'name' | 'date'>('name')

const { data, state, error, reload } = useAsyncData(
  () => folderRepository.getChildren(folderId.value),
  { emptyWhen: (result) => result.subfolders.length === 0 && result.files.length === 0 },
)

watch(folderId, () => reload())

const sortedSubfolders = computed<Folder[]>(() =>
  [...(data.value?.subfolders ?? [])].sort((a, b) => a.name.localeCompare(b.name)),
)
const sortedFiles = computed<DocumentFile[]>(() => {
  const files = [...(data.value?.files ?? [])]
  if (sortBy.value === 'date') return files.sort((a, b) => b.updatedAt.localeCompare(a.updatedAt))
  return files.sort((a, b) => a.name.localeCompare(b.name))
})

const newFolderOpened = ref(false)
const uploadOpened = ref(false)

async function onFolderAction(action: string, folder: Folder) {
  if (action === 'open') router.push({ name: 'documents', params: { folderId: folder.id } })
  else if (action === 'new-subfolder') {
    const name = window.prompt('Nom du sous-dossier ?')
    if (name) {
      await folderRepository.createFolder(folder.id, name)
      reload()
    }
  } else if (action === 'rename') {
    const name = window.prompt('Nouveau nom ?', folder.name)
    if (name) {
      await folderRepository.rename(folder.id, name)
      reload()
    }
  } else if (action === 'delete') {
    if (window.confirm(`Supprimer le dossier "${folder.name}" ?`)) {
      await folderRepository.remove(folder.id)
      reload()
    }
  }
}

async function onFileAction(action: string, file: DocumentFile) {
  if (action === 'open') router.push({ name: 'file', params: { fileId: file.id } })
  else if (action === 'favorite') {
    await documentRepository.toggleFavorite(file.id)
    reload()
  } else if (action === 'rename') {
    const name = window.prompt('Nouveau nom ?', file.name)
    if (name) {
      await documentRepository.rename(file.id, name)
      reload()
    }
  } else if (action === 'delete') {
    if (window.confirm(`Supprimer "${file.name}" ?`)) {
      await documentRepository.remove(file.id)
      reload()
    }
  } else if (action === 'details' || action === 'versions') {
    router.push({ name: 'file', params: { fileId: file.id } })
  }
}

async function createFolder(name: string) {
  await folderRepository.createFolder(folderId.value, name)
  reload()
}

// Question sur le dossier courant (parcours 3)
const askingFolder = ref(false)
const folderAnswer = ref<string | null>(null)
const folderSources = ref<DocumentSource[]>([])

async function askFolderQuestion(question: string, recursive: boolean) {
  askingFolder.value = true
  folderAnswer.value = null
  const response = await documentRepository.askQuestion({
    question,
    // At the root there is no single folder id to scope to - fall back to
    // searching across everything the user has access to.
    scope: folderId.value ? { type: 'folder', id: folderId.value, recursive } : { type: 'all' },
  })
  folderAnswer.value = response.answer
  folderSources.value = response.sources
  askingFolder.value = false
}

const fileNames = computed<Record<string, string>>(() =>
  Object.fromEntries((data.value?.files ?? []).map((f) => [f.id, f.name])),
)
</script>

<template>
  <div class="flex flex-col gap-4">
    <LoadingState v-if="state === 'loading'" label="Chargement du dossier…" />

    <EmptyState v-else-if="state === 'error'" title="Impossible de charger ce dossier" :description="error ?? undefined" icon="fr-icon-error-warning-line">
      <button type="button" class="fr-btn fr-btn--secondary" @click="reload">Réessayer</button>
    </EmptyState>

    <template v-else-if="data">
      <QuestionBox
        title="Poser une question sur ce dossier"
        show-recursive-option
        :loading="askingFolder"
        :answer="folderAnswer"
        :sources="folderSources"
        :file-names="fileNames"
        @ask="askFolderQuestion"
      />

      <FolderBreadcrumb v-if="data.folder" :folder="data.folder" />

      <div class="flex items-center justify-between flex-wrap gap-3">
        <h1 class="fr-h3 fr-mb-0">{{ data.folder?.name ?? 'Mes documents' }}</h1>
        <div class="flex gap-2">
          <button type="button" class="fr-btn fr-icon-add-line fr-btn--icon-left" @click="newFolderOpened = true">Nouveau</button>
          <button type="button" class="fr-btn fr-btn--secondary fr-icon-upload-line fr-btn--icon-left" @click="uploadOpened = true">Importer</button>
        </div>
      </div>

      <EmptyState
        v-if="state === 'empty'"
        title="Aucun document"
        description="Ce dossier ne contient encore aucun document."
        icon="fr-icon-folder-2-line"
      >
        <button type="button" class="fr-btn" @click="uploadOpened = true">Importer un document</button>
      </EmptyState>

      <template v-else>
        <div class="flex justify-end">
          <label class="fr-text--sm flex items-center gap-2">
            Trier par
            <select v-model="sortBy" class="fr-select !w-auto !py-1">
              <option value="name">Nom</option>
              <option value="date">Date de modification</option>
            </select>
          </label>
        </div>

        <FileFolderTable
          :folders="sortedSubfolders"
          :files="sortedFiles"
          @folder-action="onFolderAction"
          @file-action="onFileAction"
        />
      </template>
    </template>

    <NewFolderModal v-model:opened="newFolderOpened" @create="createFolder" />
    <UploadModal v-model:opened="uploadOpened" @imported="reload" />
  </div>
</template>
