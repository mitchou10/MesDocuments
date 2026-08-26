<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LoadingState from '@/components/common/LoadingState.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import PdfViewerMock from '@/components/media/PdfViewerMock.vue'
import AudioPlayerMock from '@/components/media/AudioPlayerMock.vue'
import VideoPlayerMock from '@/components/media/VideoPlayerMock.vue'
import QuestionBox from '@/components/agent/QuestionBox.vue'
import ShareModal from '@/components/sharing/ShareModal.vue'
import PermissionsList from '@/components/permissions/PermissionsList.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { documentRepository } from '@/repositories'
import type { DocumentSource } from '@/types'
import { formatBytes, formatDate } from '@/utils/format'
import { labelForFileKind } from '@/utils/fileIcon'

const route = useRoute()
const router = useRouter()
const fileId = computed(() => route.params.fileId as string)

const { data: file, state, error, reload: reloadFile } = useAsyncData(() => documentRepository.getDocument(fileId.value))
const { data: summary, reload: reloadSummary } = useAsyncData(() => documentRepository.getSummary(fileId.value))
const { data: versions, reload: reloadVersions } = useAsyncData(() => documentRepository.getVersions(fileId.value))
const { data: transcript, reload: reloadTranscript } = useAsyncData(() => documentRepository.getTranscript(fileId.value))

watch(fileId, () => {
  reloadFile()
  reloadSummary()
  reloadVersions()
  reloadTranscript()
  activeTab.value = 0
})

const activeTab = ref(0)
const shareOpened = ref(false)

const pdfPage = ref(1)
const pdfBbox = ref<[number, number, number, number] | undefined>(undefined)
const seekToMs = ref<number | undefined>(undefined)

watch(
  () => route.query,
  (query) => {
    if (query.page) {
      pdfPage.value = Number(query.page)
      activeTab.value = 0
    }
    if (query.bbox && typeof query.bbox === 'string') {
      pdfBbox.value = query.bbox.split(',').map(Number) as [number, number, number, number]
    }
    if (query.startMs) {
      seekToMs.value = Number(query.startMs)
      activeTab.value = 0
    }
  },
  { immediate: true },
)

function downloadFile() {
  if (!file.value) return
  const link = document.createElement('a')
  link.href = documentRepository.getDownloadUrl(file.value.id)
  link.download = file.value.name
  document.body.appendChild(link)
  link.click()
  link.remove()
}

function goBack() {
  if (file.value) router.push({ name: 'documents', params: { folderId: file.value.folderId } })
  else router.push({ name: 'documents' })
}

// Question sur ce document (parcours 2)
const asking = ref(false)
const answer = ref<string | null>(null)
const sources = ref<DocumentSource[]>([])

async function askQuestion(question: string) {
  asking.value = true
  answer.value = null
  const response = await documentRepository.askQuestion({ question, scope: { type: 'file', id: fileId.value } })
  answer.value = response.answer
  sources.value = response.sources
  asking.value = false
}

const fileNames = computed(() => (file.value ? { [file.value.id]: file.value.name } : {}))
</script>

<template>
  <div class="flex flex-col gap-4">
    <LoadingState v-if="state === 'loading'" label="Chargement du document…" />

    <EmptyState v-else-if="state === 'error'" title="Document introuvable" :description="error ?? undefined" icon="fr-icon-error-warning-line">
      <button type="button" class="fr-btn fr-btn--secondary" @click="reloadFile">Réessayer</button>
    </EmptyState>

    <template v-else-if="file">
      <QuestionBox
        title="Poser une question sur ce document"
        modal
        :loading="asking"
        :answer="answer"
        :sources="sources"
        :file-names="fileNames"
        @ask="askQuestion"
      />

      <button type="button" class="fr-btn fr-btn--tertiary-no-outline fr-icon-arrow-left-line fr-btn--icon-left self-start" @click="goBack">
        {{ file.path.slice(1).join(' / ') || 'Mes documents' }}
      </button>

      <div class="flex items-start justify-between flex-wrap gap-3">
        <div>
          <h1 class="fr-h3 fr-mb-1v">{{ file.name }}</h1>
          <p class="fr-text--sm text-[var(--text-mention-grey)] fr-mb-0">
            {{ labelForFileKind(file.kind) }} · {{ formatBytes(file.sizeBytes) }}
          </p>
        </div>
        <div class="flex gap-2">
          <button type="button" class="fr-btn fr-btn--secondary fr-icon-download-line fr-btn--icon-left" @click="downloadFile">Télécharger</button>
          <button type="button" class="fr-btn fr-btn--secondary fr-icon-share-line fr-btn--icon-left" @click="shareOpened = true">Partager</button>
        </div>
      </div>

      <DsfrTabs v-model="activeTab" tab-list-name="Sections du document">
        <DsfrTabItem tab-id="tab-apercu" panel-id="panel-apercu">Aperçu</DsfrTabItem>
        <DsfrTabItem tab-id="tab-resume" panel-id="panel-resume">Résumé</DsfrTabItem>
        <DsfrTabItem tab-id="tab-infos" panel-id="panel-infos">Informations</DsfrTabItem>
        <DsfrTabItem tab-id="tab-versions" panel-id="panel-versions">Versions</DsfrTabItem>
        <DsfrTabItem tab-id="tab-activite" panel-id="panel-activite">Activité</DsfrTabItem>

        <DsfrTabContent tab-id="tab-apercu" panel-id="panel-apercu">
          <div class="fr-p-2w flex flex-col gap-6">
            <PdfViewerMock
              v-if="file.kind === 'pdf'"
              v-model:page="pdfPage"
              :total-pages="file.pageCount ?? 1"
              :bbox="pdfBbox"
            />
            <AudioPlayerMock
              v-else-if="file.kind === 'audio'"
              :title="file.name"
              :duration-ms="file.durationMs ?? 0"
              :transcript="transcript ?? []"
              :seek-to-ms="seekToMs"
            />
            <VideoPlayerMock
              v-else-if="file.kind === 'video'"
              :title="file.name"
              :duration-ms="file.durationMs ?? 0"
              :transcript="transcript ?? []"
              :seek-to-ms="seekToMs"
            />
            <EmptyState v-else title="Aperçu non disponible" icon="fr-icon-file-line" />
          </div>
        </DsfrTabContent>

        <DsfrTabContent tab-id="tab-resume" panel-id="panel-resume">
          <div class="fr-p-2w">
            <p v-if="summary" class="fr-mb-0">{{ summary.text }}</p>
            <EmptyState v-else title="Aucun résumé disponible" icon="fr-icon-file-line" />
          </div>
        </DsfrTabContent>

        <DsfrTabContent tab-id="tab-infos" panel-id="panel-infos">
          <dl class="fr-p-2w grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 max-w-md">
            <dt class="font-medium">Type</dt>
            <dd>{{ labelForFileKind(file.kind) }}</dd>
            <dt class="font-medium">Taille</dt>
            <dd>{{ formatBytes(file.sizeBytes) }}</dd>
            <dt class="font-medium">Créé le</dt>
            <dd>{{ formatDate(file.createdAt) }}</dd>
            <dt class="font-medium">Modifié le</dt>
            <dd>{{ formatDate(file.updatedAt) }}</dd>
            <dt class="font-medium">Emplacement</dt>
            <dd>{{ file.path.join(' / ') }}</dd>
          </dl>
          <PermissionsList :resource-id="file.id" class="fr-px-2w" />
        </DsfrTabContent>

        <DsfrTabContent tab-id="tab-versions" panel-id="panel-versions">
          <ul class="fr-p-2w flex flex-col gap-2">
            <li v-for="version in versions" :key="version.id" class="flex items-center justify-between border-b border-[var(--border-default-grey)] pb-2">
              <span>Version {{ version.versionNumber }} — {{ version.note }}</span>
              <span class="fr-text--sm text-[var(--text-mention-grey)]">{{ formatDate(version.createdAt) }} · {{ formatBytes(version.sizeBytes) }}</span>
            </li>
          </ul>
        </DsfrTabContent>

        <DsfrTabContent tab-id="tab-activite" panel-id="panel-activite">
          <div class="fr-p-2w">
            <ul class="flex flex-col gap-2 fr-text--sm">
              <li>✓ Document importé le {{ formatDate(file.createdAt) }}</li>
              <li>✓ Analyse et indexation terminées</li>
              <li>✓ Dernière modification le {{ formatDate(file.updatedAt) }}</li>
            </ul>
          </div>
        </DsfrTabContent>
      </DsfrTabs>

      <ShareModal v-model:opened="shareOpened" :resource-id="file.id" :resource-name="file.name" resource-type="file" />
    </template>
  </div>
</template>
