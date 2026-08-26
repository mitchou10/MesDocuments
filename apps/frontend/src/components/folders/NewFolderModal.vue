<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{ opened: boolean }>()
const emit = defineEmits<{
  (e: 'update:opened', value: boolean): void
  (e: 'create', name: string): void
}>()

const name = ref('')

watch(
  () => props.opened,
  (opened) => {
    if (opened) name.value = ''
  },
)

function close() {
  emit('update:opened', false)
}

function submit() {
  const trimmed = name.value.trim()
  if (!trimmed) return
  emit('create', trimmed)
  close()
}
</script>

<template>
  <DsfrModal
    :opened="opened"
    title="Nouveau dossier"
    :actions="[
      { label: 'Annuler', secondary: true, onClick: close },
      { label: 'Créer', onClick: submit },
    ]"
    @update:opened="emit('update:opened', $event)"
  >
    <DsfrInputGroup
      label="Nom du dossier"
      label-visible
      hint="Exemple : Contrats 2026"
    >
      <DsfrInput v-model="name" placeholder="Nom du dossier" @keyup.enter="submit" />
    </DsfrInputGroup>
  </DsfrModal>
</template>
