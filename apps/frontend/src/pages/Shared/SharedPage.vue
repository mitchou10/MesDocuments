<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import EmptyState from '@/components/common/EmptyState.vue'
import { mockFiles } from '@/mocks'
import { mockShares } from '@/mocks/permissions'
import { formatRelativeDate } from '@/utils/format'
import { iconForFileKind } from '@/utils/fileIcon'

const router = useRouter()

const sharedFiles = computed(() =>
  mockFiles.filter((file) => (mockShares[file.id] ?? []).length > 0).map((file) => ({ file, shares: mockShares[file.id] })),
)

function open(fileId: string) {
  router.push({ name: 'file', params: { fileId } })
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <h1 class="fr-h3 fr-mb-0">Partagés</h1>

    <EmptyState v-if="sharedFiles.length === 0" title="Aucun document partagé" icon="fr-icon-share-line" />

    <ul v-else class="flex flex-col gap-2">
      <li v-for="{ file, shares } in sharedFiles" :key="file.id">
        <button type="button" class="w-full text-left rounded-sm border border-[var(--border-default-grey)] p-3 flex items-center justify-between gap-3 hover:bg-[var(--background-alt-blue-france)]" @click="open(file.id)">
          <span class="flex items-center gap-2">
            <span :class="iconForFileKind(file.kind)" aria-hidden="true" />
            {{ file.name }}
          </span>
          <span class="fr-text--sm text-[var(--text-mention-grey)]">
            Partagé avec {{ shares.length }} personne{{ shares.length > 1 ? 's' : '' }} · {{ formatRelativeDate(file.updatedAt) }}
          </span>
        </button>
      </li>
    </ul>
  </div>
</template>
