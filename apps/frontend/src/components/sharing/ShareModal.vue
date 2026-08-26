<script setup lang="ts">
import { ref, watch } from 'vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { sharingRepository } from '@/repositories'
import type { PermissionLevel } from '@/types'

const props = defineProps<{
  opened: boolean
  resourceId: string
  resourceName: string
  resourceType: 'file' | 'folder'
}>()
const emit = defineEmits<{ (e: 'update:opened', value: boolean): void }>()

const { data: shares, reload } = useAsyncData(() => sharingRepository.getShares(props.resourceId))

watch(
  () => [props.opened, props.resourceId],
  () => {
    if (props.opened) reload()
  },
)

const newPrincipalName = ref('')
const newLevel = ref<PermissionLevel>('reader')

function close() {
  emit('update:opened', false)
}

async function addShare() {
  const name = newPrincipalName.value.trim()
  if (!name) return
  await sharingRepository.addShare({
    resourceId: props.resourceId,
    resourceType: props.resourceType,
    principal: { kind: 'user', id: `mock-${Date.now()}`, name },
    level: newLevel.value,
  })
  newPrincipalName.value = ''
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
        <DsfrInputGroup label="Utilisateur ou groupe" label-visible>
          <DsfrInput v-model="newPrincipalName" placeholder="Nom" @keyup.enter="addShare" />
        </DsfrInputGroup>
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
        <button type="button" class="fr-btn self-start" @click="addShare">Ajouter</button>
      </div>
    </div>
  </DsfrModal>
</template>
