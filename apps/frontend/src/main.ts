import '@gouvfr/dsfr/dist/dsfr.min.css'
import '@gouvfr/dsfr/dist/utility/icons/icons.css'
import '@gouvminint/vue-dsfr/dist/vue-dsfr.css'
import './style.css'

import VueDsfr from '@gouvminint/vue-dsfr'
import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

const app = createApp(App)

app.use(createPinia())
app.use(VueDsfr)

// L'état d'authentification doit être connu AVANT d'installer le router : le
// premier garde de navigation en dépend pour décider de rediriger vers
// Keycloak ou de laisser passer.
const authStore = useAuthStore()
authStore.initialize().finally(() => {
  app.use(router)
  app.mount('#app')
})
