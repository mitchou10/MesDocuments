<script setup lang="ts">
import { computed } from 'vue'
import type { Folder } from '@/types'

const props = defineProps<{ folder: Folder }>()

// path already excludes the current folder's own name; rebuild ids on the fly
// is unnecessary here since navigation only ever needs the immediate parent
// chain, which the router resolves through folderId.
const links = computed(() => {
  const crumbs = props.folder.path.map((name) => ({ text: name }))
  crumbs.push({ text: props.folder.name })
  return crumbs.map((crumb, index) =>
    index === crumbs.length - 1 ? crumb : { ...crumb, to: index === 0 ? '/documents' : undefined },
  )
})
</script>

<template>
  <DsfrBreadcrumb navigation-label="Fil d'Ariane" :links="links" />
</template>
