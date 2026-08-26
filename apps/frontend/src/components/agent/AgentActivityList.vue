<script setup lang="ts">
import type { AgentActivity } from '@/types'

defineProps<{ activities: AgentActivity[] }>()
</script>

<template>
  <ul class="flex flex-col gap-1 fr-text--sm">
    <li v-for="activity in activities" :key="activity.id" class="flex items-center gap-2">
      <span
        :class="activity.status === 'done' ? 'fr-icon-checkbox-circle-fill text-[var(--text-default-success)]' : 'fr-icon-refresh-line animate-spin text-[var(--text-mention-grey)]'"
        aria-hidden="true"
      />
      {{ activity.label }}
    </li>
  </ul>
</template>
