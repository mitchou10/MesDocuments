import type { UiState } from '@/types'
import { ref, shallowRef } from 'vue'

export function useAsyncData<T>(loader: () => Promise<T>, options: { emptyWhen?: (data: T) => boolean } = {}) {
  const data = shallowRef<T | null>(null)
  const state = ref<UiState>('loading')
  const error = ref<string | null>(null)

  async function load() {
    state.value = 'loading'
    error.value = null
    try {
      const result = await loader()
      data.value = result
      state.value = options.emptyWhen?.(result) ? 'empty' : 'idle'
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Une erreur est survenue'
      state.value = 'error'
    }
  }

  load()

  return { data, state, error, reload: load }
}
