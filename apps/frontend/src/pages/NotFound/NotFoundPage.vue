<script setup lang="ts">
import { useRouter } from 'vue-router'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()
</script>

<template>
  <EmptyState title="Page introuvable" description="La page que vous cherchez n'existe pas ou plus." icon="fr-icon-question-line">
    <button type="button" class="fr-btn" @click="router.push('/documents')">Retour à mes documents</button>
  </EmptyState>
</template>
