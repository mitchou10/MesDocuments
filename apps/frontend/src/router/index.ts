import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/documents',
    },
    {
      path: '/documents/:folderId?',
      name: 'documents',
      component: () => import('@/pages/Files/FilesPage.vue'),
    },
    {
      path: '/files/:fileId',
      name: 'file',
      component: () => import('@/pages/File/FilePage.vue'),
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('@/pages/Search/SearchPage.vue'),
    },
    {
      path: '/assistant',
      name: 'assistant',
      component: () => import('@/pages/Assistant/AssistantPage.vue'),
    },
    {
      path: '/shared',
      name: 'shared',
      component: () => import('@/pages/Shared/SharedPage.vue'),
    },
    {
      path: '/favorites',
      name: 'favorites',
      component: () => import('@/pages/Favorites/FavoritesPage.vue'),
    },
    {
      path: '/recent',
      name: 'recent',
      component: () => import('@/pages/Recent/RecentPage.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/pages/NotFound/NotFoundPage.vue'),
    },
  ],
})

// L'authentification est déjà résolue avant que le router ne soit installé
// (voir main.ts) : ce garde n'a donc qu'à lire l'état, jamais à l'attendre.
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!auth.isAuthenticated) {
    auth.login(to.fullPath)
    return false
  }
  return true
})

export default router
