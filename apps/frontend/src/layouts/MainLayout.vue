<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const navItems = [
  { label: 'Mes documents', to: '/documents', icon: 'fr-icon-folder-2-line' },
  { label: 'Assistant', to: '/assistant', icon: 'fr-icon-chat-3-line' },
  { label: 'Partagés', to: '/shared', icon: 'fr-icon-share-line' },
  { label: 'Favoris', to: '/favorites', icon: 'fr-icon-star-line' },
  { label: 'Récents', to: '/recent', icon: 'fr-icon-time-line' },
]

const isActive = (to: string) => route.path === to || route.path.startsWith(`${to}/`)
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <DsfrHeader
      service-title="MesDocuments"
      service-description="Gestion documentaire intelligente"
      home-to="/documents"
      :quick-links="[{ label: 'Camille Bernard', icon: 'fr-icon-account-circle-line', to: '/documents' }]"
    />

    <div class="fr-container flex-1 w-full py-6 flex gap-8 items-start">
      <nav class="hidden md:block w-64 shrink-0" aria-label="Navigation principale">
        <DsfrSideMenu heading-title="MesDocuments" :menu-items="[]">
          <ul class="fr-sidemenu__list">
            <li v-for="item in navItems" :key="item.to" class="fr-sidemenu__item" :class="{ 'fr-sidemenu__item--active': isActive(item.to) }">
              <router-link class="fr-sidemenu__link" :to="item.to" :aria-current="isActive(item.to) ? 'page' : undefined">
                {{ item.label }}
              </router-link>
            </li>
            <li class="fr-sidemenu__item">
              <span class="fr-sidemenu__link fr-sidemenu__link--disabled opacity-60">Corbeille</span>
            </li>
          </ul>
        </DsfrSideMenu>
      </nav>

      <main id="main-content" class="flex-1 min-w-0">
        <router-view />
      </main>
    </div>

    <DsfrFooter
      logo-text="MesDocuments"
      description="Prototype frontend — données mockées"
    />
  </div>
</template>
