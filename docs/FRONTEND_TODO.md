# MesDocuments — TODO Frontend

Plan d'exécution dérivé de [FRONTEND_SPEC.md](./FRONTEND_SPEC.md). À cocher au fur et à mesure.

## Phase 0 — Bootstrap projet

- [x] Initialiser le projet Vite (Vue 3 + TypeScript) dans `apps/frontend`
- [x] Installer Vue Router, Pinia
- [x] Installer le Design System de l'État (DSFR) et sa config Vite/CSS
- [ ] Configurer ESLint/Prettier/tsconfig strict
- [x] Vérifier que `npm run dev` démarre une page vide fonctionnelle

## Phase 1 — Fondations (types, mocks, repositories)

- [x] Définir les types TypeScript (`types/`) : User, Group, Folder, File, FileVersion,
      Permission, Share, DocumentSummary, DocumentChunk, DocumentSource, SearchResult,
      SearchRequest, SearchResponse, QueryRequest, QueryResponse, AgentMessage, AgentTask,
      AgentActivity, QueryScope
- [x] Écrire les jeux de données mockées (`mocks/`) : arborescence Clients/ACME/Total,
      Finance, RH avec fichiers PDF/audio/vidéo réalistes
- [x] Définir les interfaces repository (`repositories/`) : DocumentRepository,
      FolderRepository, SearchRepository, SharingRepository, PermissionRepository,
      AgentRepository
- [x] Implémenter les Mock*Repository correspondants (avec latence simulée réaliste)

## Phase 2 — Layout & navigation

- [x] Layout principal DSFR (header + sidebar + zone de contenu)
- [x] Router avec les routes : `/`, `/documents`, `/documents/:folderId`, `/files/:fileId`,
      `/search`, `/assistant`, `/shared`, `/favorites`, `/recent`
- [x] Sidebar : Mes documents / Partagés / Favoris / Récents / Corbeille
- [x] Breadcrumb dynamique lié à la route

## Phase 3 — Gestion documentaire (parcours 1)

- [x] Page "Mes documents" : liste dossiers/fichiers, tri, actions
- [x] Navigation dossier → sous-dossier → retour parent (piloté par la route)
- [x] Modal "Nouveau dossier" (DSFR) avec mise à jour du mock en mémoire
- [x] UX Upload (zone drag&drop + sélection) avec états : sélectionné, upload,
      terminé, erreur, analyse en cours (texte extrait / résumé / indexation)
- [x] Actions fichiers (ouvrir, télécharger, renommer, déplacer, partager, favoris,
      détails, versions, supprimer) et dossiers (ouvrir, renommer, partager,
      créer sous-dossier, supprimer) — mockées (renommer/déplacer/télécharger
      restent des stubs `window.prompt`/no-op à raffiner)
- [x] États UI : loading / empty / error / forbidden / not found / processing
      (forbidden pas encore illustré dans un écran concret)

## Phase 4 — Page fichier & viewers (parcours 2)

- [x] Page fichier avec tabs : Aperçu / Résumé / Informations / Versions / Activité
- [x] Viewer PDF mock : pagination, navigation, zoom, zone surlignée,
      fonction `openPdfAt({ page, bbox })` (via query params `page`/`bbox`)
- [x] Lecteur audio mock avec transcription et positionnement par timestamp
- [x] Lecteur vidéo mock avec transcription et positionnement par `startMs`/`endMs`
- [x] Composant `DocumentSources` (rendu PDF / audio / vidéo)

## Phase 5 — Questions & recherche (parcours 2 & 3)

- [x] "Poser une question sur ce document" → réponse mock + sources cliquables
      ouvrant le viewer à la bonne page
- [x] "Poser une question sur ce dossier" (+ option sous-dossiers) → réponse
      multi-sources
- [x] Modèle `QueryScope` utilisé de façon cohérente dans les composants
- [x] Page de recherche : champ, filtres (type ; emplacement/date/propriétaire
      restent à ajouter), résultats avec extrait et tag keyword/sémantique/hybride

## Phase 6 — Partage & permissions (parcours 4)

- [x] Modal de partage (liste des accès + ajout utilisateur/groupe + niveau de
      permission)
- [x] Affichage des permissions : accès direct / hérité / refusé (lecture seule,
      pas de logique métier côté frontend)

## Phase 7 — Assistant documentaire (parcours 5)

- [x] Page `/assistant` : interface conversationnelle
- [x] Composant `AgentActivity` (étapes ✓/⏳, jamais de chain-of-thought)
- [x] Contexte agent depuis un fichier ou un dossier (scope transmis via query
      params `folderId`/`fileId`) — reste à ajouter le bouton "Assistant"
      contextuel dans les pages Dossier/Fichier
- [x] Réponse finale de l'agent avec sources cliquables

## Phase 8 — Pages complémentaires

- [x] `/shared` avec données mockées
- [x] `/favorites` avec données mockées
- [x] `/recent` avec données mockées

## Phase 9 — Responsive & accessibilité

- [ ] Vérification desktop / tablette / mobile (navigation, liste fichiers,
      assistant, modales) — sidebar masquée en dessous de `md`, pas encore de
      nav mobile de repli
- [ ] Audit accessibilité : navigation clavier, focus, labels, contrastes, ARIA

## Phase 10 — Revue finale

- [ ] Rejouer les 5 parcours prioritaires de bout en bout dans un vrai navigateur
- [x] Vérifier qu'aucune dépendance backend réelle n'a été introduite
- [x] `pnpm install && pnpm dev` fonctionne à froid (testé également via Docker,
      cf. `Dockerfile` + `docker-compose.yml` à la racine, target `dev` avec
      Compose Watch)
- [x] Documenter dans le README frontend comment brancher plus tard une vraie API
      (remplacement des Mock*Repository)
