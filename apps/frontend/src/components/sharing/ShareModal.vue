<script setup lang="ts">
import { ref, watch } from 'vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { sharingRepository, userRepository } from '@/repositories'
import type { PermissionLevel, PrincipalRef } from '@/types'

const props = defineProps<{
  opened: boolean
  resourceId: string
  resourceName: string
  resourceType: 'file' | 'folder'
}>()
const emit = defineEmits<{ (e: 'update:opened', value: boolean): void }>()

const { data: shares, reload } = useAsyncData(() =>
  sharingRepository.getShares(props.resourceId, props.resourceType),
)

watch(
  () => [props.opened, props.resourceId],
  () => {
    if (props.opened) {
      reload()
      searchQuery.value = ''
      searchResults.value = []
      selectedPrincipal.value = null
    }
  },
)

const searchQuery = ref('')
const searchResults = ref<PrincipalRef[]>([])
const selectedPrincipal = ref<PrincipalRef | null>(null)
const newLevel = ref<PermissionLevel>('reader')
let searchToken = 0

function close() {
  emit('update:opened', false)
}

async function onSearchInput() {
  selectedPrincipal.value = null
  const query = searchQuery.value.trim()
  if (query.length < 2) {
    searchResults.value = []
    return
  }
  const token = ++searchToken
  const results = await userRepository.search(query)
  if (token === searchToken) searchResults.value = results
}

function selectPrincipal(principal: PrincipalRef) {
  selectedPrincipal.value = principal
  searchQuery.value = principal.name
  searchResults.value = []
}

async function addShare() {
  if (!selectedPrincipal.value) return
  await sharingRepository.addShare({
    resourceId: props.resourceId,
    resourceType: props.resourceType,
    principal: selectedPrincipal.value,
    level: newLevel.value,
  })
  searchQuery.value = ''
  selectedPrincipal.value = null
  reload()
}

async function removeShare(shareId: string) {
  await sharingRepository.removeShare(shareId)
  reload()
}
</script>

<template>
  <DsfrModal
    :opened="opened"
    :title="`Partager « ${resourceName} »`"
    size="md"
    :actions="[{ label: 'Fermer', onClick: close }]"
    @update:opened="emit('update:opened', $event)"
  >
    <div class="flex flex-col gap-4">
      <div>
        <p class="fr-text--sm font-medium fr-mb-1w">Personnes ayant accès</p>
        <ul class="flex flex-col gap-2">
          <li v-for="share in shares" :key="share.id" class="flex items-center justify-between gap-2">
            <span class="flex items-center gap-2">
              <span :class="share.principal.kind === 'group' ? 'fr-icon-team-line' : 'fr-icon-account-line'" aria-hidden="true" />
              {{ share.principal.name }}
            </span>
            <span class="flex items-center gap-3">
              <DsfrTag :label="share.level === 'editor' ? 'Éditeur' : 'Lecteur'" small />
              <button type="button" class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-icon-close-line" aria-label="Retirer l'accès" @click="removeShare(share.id)" />
            </span>
          </li>
          <li v-if="shares && shares.length === 0" class="fr-text--sm text-[var(--text-mention-grey)]">Aucun partage pour le moment.</li>
        </ul>
      </div>

      <div class="border-t border-[var(--border-default-grey)] pt-4 flex flex-col gap-3">
        <DsfrInputGroup label="Utilisateur" label-visible>
          <DsfrInput v-model="searchQuery" placeholder="Rechercher par nom ou e-mail" @input="onSearchInput" />
        </DsfrInputGroup>
        <ul v-if="searchResults.length" class="flex flex-col gap-1 rounded-sm border border-[var(--border-default-grey)]">
          <li v-for="principal in searchResults" :key="principal.id">
            <button
              type="button"
              class="fr-btn fr-btn--tertiary-no-outline w-full justify-start"
              @click="selectPrincipal(principal)"
            >
              {{ principal.name }}
            </button>
          </li>
        </ul>
        <DsfrRadioButtonSet
          name="permission-level"
          legend="Permission"
          :options="[
            { label: 'Lecteur', value: 'reader' },
            { label: 'Éditeur', value: 'editor' },
          ]"
          :model-value="newLevel"
          @update:model-value="(v: string) => (newLevel = v as PermissionLevel)"
        />
        <button type="button" class="fr-btn self-start" :disabled="!selectedPrincipal" @click="addShare">
          Ajouter
        </button>
      </div>
    </div>
  </DsfrModal>
</template>
