<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import EmptyState from '@/components/common/EmptyState.vue'
import { db } from '@/repositories/mockDb'
import { formatRelativeDate } from '@/utils/format'
import { iconForFileKind } from '@/utils/fileIcon'

const router = useRouter()
const favoriteFiles = computed(() => db.files.filter((f) => f.isFavorite))

function open(fileId: string) {
  router.push({ name: 'file', params: { fileId } })
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <h1 class="fr-h3 fr-mb-0">Favoris</h1>

    <EmptyState v-if="favoriteFiles.length === 0" title="Aucun favori" description="Ajoutez des documents à vos favoris pour les retrouver ici." icon="fr-icon-star-line" />

    <ul v-else class="flex flex-col gap-2">
      <li v-for="file in favoriteFiles" :key="file.id">
        <button type="button" class="w-full text-left rounded-sm border border-[var(--border-default-grey)] p-3 flex items-center justify-between gap-3 hover:bg-[var(--background-alt-blue-france)]" @click="open(file.id)">
          <span class="flex items-center gap-2">
            <span :class="iconForFileKind(file.kind)" aria-hidden="true" />
            {{ file.name }}
          </span>
          <span class="fr-text--sm text-[var(--text-mention-grey)]">{{ file.path.join(' / ') }} · {{ formatRelativeDate(file.updatedAt) }}</span>
        </button>
      </li>
    </ul>
  </div>
</template>
