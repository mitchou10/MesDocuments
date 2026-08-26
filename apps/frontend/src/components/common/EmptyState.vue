<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    description?: string
    icon?: string
  }>(),
  { icon: 'fr-icon-inbox-line' },
)
</script>

<template>
  <div class="flex flex-col items-center text-center gap-3 py-16 px-4">
    <span :class="icon" class="text-4xl text-[var(--text-mention-grey)]" aria-hidden="true" />
    <p class="fr-text--lead fr-mb-0">{{ title }}</p>
    <p v-if="description" class="fr-text--sm text-[var(--text-mention-grey)] fr-mb-0 max-w-md">{{ description }}</p>
    <div v-if="$slots.default" class="fr-mt-2w">
      <slot />
    </div>
  </div>
</template>
