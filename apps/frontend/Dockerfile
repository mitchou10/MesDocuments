# syntax=docker/dockerfile:1

FROM node:22-alpine AS base
WORKDIR /app
RUN corepack enable

FROM base AS deps
COPY package.json pnpm-lock.yaml* ./
# --ignore-scripts : le script preinstall de @gouvfr/dsfr sert uniquement à
# son installeur interactif (pnpm create @gouvfr/dsfr), inutile ici puisqu'on
# importe directement les CSS précompilés du paquet.
RUN pnpm install --frozen-lockfile --ignore-scripts

# --- Développement : serveur Vite avec hot-reload -------------------------
FROM deps AS dev
COPY --chown=node:node . .
RUN chown -R node:node /app
USER node
EXPOSE 5173
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1:5173/ || exit 1
CMD ["pnpm", "dev", "--host", "0.0.0.0"]

# --- Build de production ---------------------------------------------------
FROM deps AS build
COPY . .
RUN pnpm build

# --- Production : fichiers statiques servis par Nginx (non-root) -----------
FROM nginxinc/nginx-unprivileged:1.27-alpine AS production
COPY --from=build --chown=nginx:nginx /app/dist /usr/share/nginx/html
COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf
USER nginx
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8080/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
