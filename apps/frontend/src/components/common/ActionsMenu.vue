<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

export interface ActionMenuItem {
  key: string
  label: string
  icon?: string
  danger?: boolean
}

const props = defineProps<{ items: ActionMenuItem[]; label: string }>()
const emit = defineEmits<{ (e: 'select', key: string): void }>()

const open = ref(false)
const rootEl = ref<HTMLElement | null>(null)

function toggle() {
  open.value = !open.value
}

function select(item: ActionMenuItem) {
  open.value = false
  emit('select', item.key)
}

function onClickOutside(event: MouseEvent) {
  if (rootEl.value && !rootEl.value.contains(event.target as Node)) open.value = false
}

onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div ref="rootEl" class="relative inline-block">
    <button
      type="button"
      class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-icon-more-line"
      :aria-label="label"
      aria-haspopup="true"
      :aria-expanded="open"
      @click.stop="toggle"
    />
    <ul
      v-if="open"
      class="absolute right-0 z-20 mt-1 min-w-[12rem] rounded-sm border border-[var(--border-default-grey)] bg-[var(--background-default-grey)] shadow-lg py-1"
      role="menu"
    >
      <li v-for="item in props.items" :key="item.key" role="none">
        <button
          type="button"
          role="menuitem"
          class="w-full text-left px-4 py-2 text-sm hover:bg-[var(--background-alt-blue-france)] flex items-center gap-2"
          :class="{ 'text-[var(--text-default-error)]': item.danger }"
          @click="select(item)"
        >
          <span v-if="item.icon" :class="item.icon" aria-hidden="true" />
          {{ item.label }}
        </button>
      </li>
    </ul>
  </div>
</template>
