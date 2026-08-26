import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export interface AuthUser {
  sub: string
  username: string | null
  email: string | null
  name: string | null
  roles: string[]
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)

  const isAuthenticated = computed(() => user.value !== null)
  const displayName = computed(() => user.value?.name ?? user.value?.username ?? '')

  async function initialize(): Promise<void> {
    try {
      const response = await fetch('/api/v1/auth/me', { credentials: 'same-origin' })
      user.value = response.ok ? ((await response.json()) as AuthUser) : null
    } catch {
      user.value = null
    }
  }

  function login(returnTo: string): void {
    window.location.href = `/api/v1/auth/login?return_to=${encodeURIComponent(returnTo)}`
  }

  function logout(): void {
    window.location.href = '/api/v1/auth/logout'
  }

  return { user, isAuthenticated, displayName, initialize, login, logout }
})
