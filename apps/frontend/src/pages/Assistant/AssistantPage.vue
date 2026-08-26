<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import AgentActivityList from '@/components/agent/AgentActivityList.vue'
import DocumentSources from '@/components/documents/DocumentSources.vue'
import { agentRepository } from '@/repositories'
import { mockFiles } from '@/mocks'
import type { AgentMessage, QueryScope } from '@/types'

const route = useRoute()

// Contexte optionnel transmis depuis une page fichier/dossier (parcours 5).
const scope: QueryScope = route.query.folderId
  ? { type: 'folder', id: String(route.query.folderId), recursive: true }
  : route.query.fileId
    ? { type: 'file', id: String(route.query.fileId) }
    : { type: 'all' }

const scopeLabel =
  scope.type === 'all' ? 'Tous mes documents' : scope.type === 'folder' ? 'Ce dossier (avec sous-dossiers)' : 'Ce document'

const messages = ref<AgentMessage[]>([])
const question = ref('')
const asking = ref(false)

const fileNames: Record<string, string> = Object.fromEntries(mockFiles.map((f) => [f.id, f.name]))

async function send() {
  const text = question.value.trim()
  if (!text) return
  question.value = ''

  messages.value.push({ id: `u-${Date.now()}`, role: 'user', text, createdAt: new Date().toISOString() })
  asking.value = true

  const { message } = await agentRepository.query({ question: text, scope, history: messages.value })
  messages.value.push(message)
  asking.value = false
}
</script>

<template>
  <div class="flex flex-col gap-4 max-w-3xl h-full">
    <div>
      <h1 class="fr-h3 fr-mb-1v">MesDocuments Assistant</h1>
      <p class="fr-text--sm text-[var(--text-mention-grey)] fr-mb-0">
        Je peux rechercher, parcourir et analyser les documents auxquels vous avez accès.
      </p>
      <DsfrTag class="fr-mt-1w" :label="`Contexte : ${scopeLabel}`" small />
    </div>

    <ul class="flex flex-col gap-4 fr-mt-2w">
      <li v-for="message in messages" :key="message.id" :class="message.role === 'user' ? 'self-end text-right' : 'self-start'">
        <div
          class="inline-block rounded-sm px-4 py-3 max-w-2xl text-left"
          :class="message.role === 'user' ? 'bg-[var(--background-action-high-blue-france)] text-white' : 'bg-[var(--background-alt-grey)]'"
        >
          <p class="fr-mb-0">{{ message.text }}</p>
        </div>
        <div v-if="message.activities" class="fr-mt-1w">
          <AgentActivityList :activities="message.activities" />
        </div>
        <div v-if="message.sources?.length" class="fr-mt-1w max-w-2xl">
          <DocumentSources :sources="message.sources" :file-names="fileNames" />
        </div>
      </li>
    </ul>

    <p v-if="asking" class="fr-text--sm text-[var(--text-mention-grey)]">
      <span class="fr-icon-refresh-line animate-spin" aria-hidden="true" /> Recherche et analyse en cours…
    </p>

    <form class="flex gap-2 fr-mt-auto pt-4" @submit.prevent="send">
      <DsfrInput v-model="question" placeholder="Trouve les contrats ACME et compare leurs conditions de résiliation." class="flex-1" />
      <button type="submit" class="fr-btn" :disabled="asking || !question.trim()">Envoyer</button>
    </form>
  </div>
</template>
