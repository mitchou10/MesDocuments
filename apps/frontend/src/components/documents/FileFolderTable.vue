<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import ActionsMenu, { type ActionMenuItem } from '@/components/common/ActionsMenu.vue'
import { folderActionItems } from '@/components/documents/folderActionItems'
import type { DocumentFile, Folder } from '@/types'
import { formatRelativeDate } from '@/utils/format'
import { iconForFileKind, labelForFileKind } from '@/utils/fileIcon'

const props = defineProps<{ folders: Folder[]; files: DocumentFile[] }>()

const emit = defineEmits<{
  (e: 'folder-action', action: string, folder: Folder): void
  (e: 'file-action', action: string, file: DocumentFile): void
}>()

const router = useRouter()

const folderActions = folderActionItems

const fileActions: ActionMenuItem[] = [
  { key: 'open', label: 'Ouvrir', icon: 'fr-icon-eye-line' },
  { key: 'download', label: 'Télécharger', icon: 'fr-icon-download-line' },
  { key: 'rename', label: 'Renommer', icon: 'fr-icon-edit-line' },
  { key: 'move', label: 'Déplacer', icon: 'fr-icon-folder-2-line' },
  { key: 'share', label: 'Partager', icon: 'fr-icon-share-line' },
  { key: 'favorite', label: 'Favoris', icon: 'fr-icon-star-line' },
  { key: 'details', label: 'Détails', icon: 'fr-icon-information-line' },
  { key: 'versions', label: 'Versions', icon: 'fr-icon-time-line' },
  { key: 'delete', label: 'Supprimer', icon: 'fr-icon-delete-bin-line', danger: true },
]

const rows = computed(() => [
  ...props.folders.map((folder) => ({ type: 'folder' as const, folder })),
  ...props.files.map((file) => ({ type: 'file' as const, file })),
])

function openFolder(folder: Folder) {
  router.push({ name: 'documents', params: { folderId: folder.id } })
}

function openFile(file: DocumentFile) {
  router.push({ name: 'file', params: { fileId: file.id } })
}
</script>

<template>
  <table class="fr-table w-full">
    <caption class="sr-only">Contenu du dossier</caption>
    <thead>
      <tr>
        <th scope="col">Nom</th>
        <th scope="col">Type</th>
        <th scope="col">Modifié</th>
        <th scope="col"><span class="sr-only">Actions</span></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="row in rows" :key="row.type === 'folder' ? `f-${row.folder.id}` : `d-${row.file.id}`">
        <td>
          <button
            type="button"
            class="fr-btn fr-btn--tertiary-no-outline flex items-center gap-2 !justify-start"
            @click="row.type === 'folder' ? openFolder(row.folder) : openFile(row.file)"
          >
            <span
              :class="row.type === 'folder' ? 'fr-icon-folder-2-line' : iconForFileKind(row.file.kind)"
              class="text-lg"
              aria-hidden="true"
            />
            <span class="truncate max-w-xs">{{ row.type === 'folder' ? row.folder.name : row.file.name }}</span>
          </button>
        </td>
        <td>{{ row.type === 'folder' ? 'Dossier' : labelForFileKind(row.file.kind) }}</td>
        <td>{{ formatRelativeDate(row.type === 'folder' ? row.folder.updatedAt : row.file.updatedAt) }}</td>
        <td class="text-right">
          <ActionsMenu
            :label="`Actions pour ${row.type === 'folder' ? row.folder.name : row.file.name}`"
            :items="row.type === 'folder' ? folderActions : fileActions"
            @select="(action) => (row.type === 'folder' ? emit('folder-action', action, row.folder) : emit('file-action', action, row.file))"
          />
        </td>
      </tr>
    </tbody>
  </table>
</template>
