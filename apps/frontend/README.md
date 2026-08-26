# MesDocuments — Frontend

Prototype frontend de MesDocuments (Vue 3 + TypeScript + Vite + DSFR + Tailwind
pour les utilitaires de mise en page). Voir [../../docs/FRONTEND_SPEC.md](../../docs/FRONTEND_SPEC.md)
pour la spécification complète et [../../docs/FRONTEND_TODO.md](../../docs/FRONTEND_TODO.md)
pour l'avancement.

Cette phase est strictement frontend : toutes les données sont mockées
(`src/mocks/`), il n'y a pas de backend, pas d'API réelle, pas de LLM réel.

## Lancer en local

```bash
pnpm install
pnpm dev
```

## Lancer avec Docker (hot-reload)

```bash
docker compose watch frontend
# ou, sans watch :
docker compose up frontend
```

L'application est servie sur http://localhost:5173.

## Build de production

```bash
pnpm build   # ou : docker build --target production -t mesdocuments-frontend .
pnpm preview
```

## Architecture

- `types/` — modèle de données du domaine (Folder, DocumentFile, SearchResult, AgentMessage…)
- `mocks/` — jeux de données fictifs (arborescence Clients/Finance/RH, permissions, chunks de recherche)
- `repositories/` — interfaces (`FolderRepository`, `DocumentRepository`, `SearchRepository`,
  `SharingRepository`, `PermissionRepository`, `AgentRepository`) + implémentations `Mock*`
- `composables/`, `components/`, `layouts/`, `pages/`, `router/` — UI Vue classique

## Brancher une vraie API plus tard

Chaque repository mock vit derrière une interface dans `src/repositories/types.ts`.
Pour brancher un backend réel :

1. Créer un `Http*Repository` par interface (ex. `HttpDocumentRepository`) qui appelle l'API.
2. Dans `src/repositories/index.ts`, remplacer l'instanciation `new Mock*Repository()`
   par `new Http*Repository()`.

Aucun composant ni aucune page ne dépend directement des mocks : tout passe par
ces interfaces, donc ce remplacement ne touche qu'un seul fichier.
