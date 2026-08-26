<script setup lang="ts">
import { useAsyncData } from '@/composables/useAsyncData'
import { permissionRepository } from '@/repositories'
import type { PermissionOrigin } from '@/types'

const props = defineProps<{ resourceId: string }>()
const { data: permissions } = useAsyncData(() => permissionRepository.getPermissions(props.resourceId))

const originLabel: Record<PermissionOrigin, string> = {
  direct: 'Accès direct',
  inherited: 'Accès hérité',
  denied: 'Accès refusé',
}

const levelLabel = { reader: 'Lecteur', editor: 'Éditeur', owner: 'Propriétaire' }
</script>

<template>
  <div v-if="permissions && permissions.length" class="fr-mt-3w">
    <p class="fr-text--sm font-medium fr-mb-1w">Permissions</p>
    <ul class="flex flex-col gap-1">
      <li v-for="(permission, index) in permissions" :key="index" class="fr-text--sm flex items-center gap-2">
        <span>{{ permission.principal.name }} →</span>
        <DsfrTag
          :label="permission.origin === 'denied' ? 'Accès refusé' : levelLabel[permission.level]"
          small
        />
        <span class="text-[var(--text-mention-grey)]">
          ({{ originLabel[permission.origin] }}{{ permission.inheritedFrom ? ` de ${permission.inheritedFrom}` : '' }})
        </span>
      </li>
    </ul>
  </div>
</template>
