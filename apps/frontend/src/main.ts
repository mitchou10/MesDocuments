import '@gouvfr/dsfr/dist/dsfr.min.css'
import '@gouvfr/dsfr/dist/utility/icons/icons.css'
import '@gouvminint/vue-dsfr/dist/vue-dsfr.css'
import './style.css'

import VueDsfr from '@gouvminint/vue-dsfr'
import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(VueDsfr)

app.mount('#app')
