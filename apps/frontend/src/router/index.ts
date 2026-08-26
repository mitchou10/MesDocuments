import { createRouter, createWebHistory } from 'vue-router'

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

export default router
