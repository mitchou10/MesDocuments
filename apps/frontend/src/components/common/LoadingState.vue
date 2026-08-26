<script setup lang="ts">
withDefaults(defineProps<{ label?: string }>(), { label: 'Chargement…' })
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-3 py-16" role="status" aria-live="polite">
    <span class="fr-icon-refresh-line fr-icon--lg animate-spin" aria-hidden="true" />
    <p class="fr-text--sm fr-mb-0">{{ label }}</p>
  </div>
</template>
