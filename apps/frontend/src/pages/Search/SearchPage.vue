<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import EmptyState from '@/components/common/EmptyState.vue'
import LoadingState from '@/components/common/LoadingState.vue'
import { searchRepository } from '@/repositories'
import type { QueryScope, SearchResult } from '@/types'
import { formatDuration } from '@/utils/format'

const route = useRoute()
const router = useRouter()

const query = ref((route.query.q as string) ?? '')
const fileKind = ref<string>('')
const scope: QueryScope = { type: 'all' }

const loading = ref(false)
const searched = ref(false)
const results = ref<SearchResult[]>([])

async function runSearch() {
  if (!query.value.trim()) return
  loading.value = true
  searched.value = true
  router.replace({ name: 'search', query: { q: query.value } })
  const response = await searchRepository.search({
    query: query.value,
    scope,
    filters: fileKind.value ? { fileKind: fileKind.value } : undefined,
  })
  results.value = response.results
  loading.value = false
}

watch(fileKind, () => {
  if (searched.value) runSearch()
})

if (query.value) runSearch()

function kindLabel(kind: SearchResult['kind']) {
  return { keyword: 'Mot-clé', semantic: 'Sémantique', hybrid: 'Hybride' }[kind]
}

function openResult(result: SearchResult) {
  const source = result.source
  const q =
    source.type === 'pdf'
      ? { page: String(source.page), ...(source.bbox ? { bbox: source.bbox.join(',') } : {}) }
      : { startMs: String(source.startMs), endMs: String(source.endMs) }
  router.push({ name: 'file', params: { fileId: result.fileId }, query: q })
}
</script>

<template>
  <div class="flex flex-col gap-4 max-w-3xl">
    <h1 class="fr-h3 fr-mb-0">Recherche</h1>

    <p class="fr-text--sm text-[var(--text-mention-grey)] fr-mb-0">
      Recherche dans : <strong>Tous mes documents</strong>
    </p>

    <DsfrSearchBar
      v-model="query"
      placeholder="Quels documents parlent de résiliation ?"
      label="Rechercher dans mes documents"
      button-text="Rechercher"
      @search="runSearch"
    />

    <div class="flex flex-wrap gap-3 items-end">
      <label class="fr-text--sm flex items-center gap-2">
        Type
        <select v-model="fileKind" class="fr-select !w-auto !py-1">
          <option value="">Tous</option>
          <option value="pdf">PDF</option>
          <option value="audio">Audio</option>
          <option value="video">Vidéo</option>
        </select>
      </label>
    </div>

    <LoadingState v-if="loading" label="Recherche en cours…" />

    <EmptyState
      v-else-if="searched && results.length === 0"
      title="Aucun résultat"
      description="Essayez une autre formulation ou élargissez le scope de recherche."
      icon="fr-icon-search-line"
    />

    <ul v-else-if="results.length" class="flex flex-col gap-3">
      <li v-for="result in results" :key="result.chunkId" class="rounded-sm border border-[var(--border-default-grey)] p-4">
        <div class="flex items-center justify-between gap-2 flex-wrap">
          <button type="button" class="fr-btn fr-btn--tertiary-no-outline font-medium" @click="openResult(result)">
            {{ result.fileName }}
          </button>
          <DsfrTag :label="kindLabel(result.kind)" small />
        </div>
        <p class="fr-text--sm text-[var(--text-mention-grey)] fr-mb-1v">
          {{ result.source.type === 'pdf' ? `Page ${result.source.page}` : `${formatDuration(result.source.startMs)} → ${formatDuration(result.source.endMs)}` }}
        </p>
        <p class="fr-mb-0">« {{ result.excerpt.trim() }} »</p>
      </li>
    </ul>
  </div>
</template>
