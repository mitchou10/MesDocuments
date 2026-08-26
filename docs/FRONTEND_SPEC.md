# MESDOCUMENTS — FRONTEND ONLY

## Mission

Construire le frontend de "MesDocuments", une application moderne de gestion documentaire.

IMPORTANT :

Cette phase est STRICTEMENT FRONTEND.

NE PAS développer :
- backend
- API backend
- FastAPI
- PostgreSQL
- Keycloak
- Qdrant
- OpenSearch
- workers
- queues
- stockage objet
- chiffrement
- LLM réel
- MCP
- A2A

Tout doit être simulé avec des données mockées.

L'objectif est de construire une expérience frontend complète et réaliste avant de commencer le backend.

---

## 1. Stack obligatoire

Utiliser :

- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia si nécessaire
- DSFR / Design System de l'État
- composants DSFR officiels autant que possible

Ne pas ajouter une autre bibliothèque UI complète.

Éviter de réinventer les composants DSFR.

Le code doit être propre, typé et maintenable.

---

## 2. Philosophie du prototype

Je veux pouvoir lancer le frontend et avoir l'impression d'utiliser une vraie application.

Les données sont fictives mais l'expérience doit être réaliste.

Les interactions doivent fonctionner :

- navigation ;
- ouverture de dossiers ;
- ouverture de fichiers ;
- recherche ;
- upload simulé ;
- partage simulé ;
- permissions simulées ;
- questions sur les documents ;
- questions sur les dossiers ;
- agent documentaire simulé ;
- sources ;
- navigation vers une page PDF ;
- navigation vers un timestamp audio/vidéo.

Aucune fonctionnalité ne doit nécessiter un backend réel.

---

## 3. Architecture

Construire une architecture frontend claire.

Proposition :

```
src/
  app/
  assets/
  components/
    dsfr/
    common/
    documents/
    folders/
    search/
    sharing/
    permissions/
    agent/
    media/
  layouts/
  pages/
    Home/
    Files/
    File/
    Folder/
    Search/
    Assistant/
    Shared/
    Favorites/
    Recent/
  router/
  stores/
  mocks/
  repositories/
  types/
  composables/
  utils/
```

Adapter cette structure si une meilleure architecture Vue est pertinente.

---

## 4. Repository pattern

Même avec des mocks, ne pas mettre les données directement dans les composants.

Créer des interfaces :

- DocumentRepository
- FolderRepository
- SearchRepository
- SharingRepository
- PermissionRepository
- AgentRepository

Exemple :

```ts
interface FolderRepository {
  getFolder(id: string): Promise<Folder>
  getChildren(id: string): Promise<FolderChildren>
}

interface DocumentRepository {
  getDocument(id: string): Promise<Document>
  getVersions(id: string): Promise<DocumentVersion[]>
}

interface SearchRepository {
  search(request: SearchRequest): Promise<SearchResponse>
}

interface AgentRepository {
  query(request: AgentQueryRequest): Promise<AgentResponse>
}
```

Implémenter uniquement :

```
MockFolderRepository
MockDocumentRepository
MockSearchRepository
MockSharingRepository
MockPermissionRepository
MockAgentRepository
```

Plus tard, ces implémentations pourront être remplacées par une API HTTP.

---

## 5. Modèle de données frontend

Créer des types TypeScript propres.

Prévoir au minimum :

- User
- Group
- Folder
- File
- FileVersion
- Permission
- Share
- DocumentSummary
- DocumentChunk
- DocumentSource
- SearchResult
- SearchRequest
- SearchResponse
- QueryRequest
- QueryResponse
- AgentMessage
- AgentTask
- AgentActivity

---

## 6. Arborescence documentaire

Créer une arborescence réaliste :

```
Mes documents
├── Clients
│   ├── ACME
│   │   ├── Contrats
│   │   │   ├── contrat-2024.pdf
│   │   │   └── avenant-2025.pdf
│   │   ├── Réunions
│   │   │   ├── reunion-janvier.mp4
│   │   │   └── reunion-fevrier.mp3
│   │   └── Documents administratifs
│   │       └── fiche-client.pdf
│   │
│   └── Total
│       └── Contrats
│
├── Finance
│   ├── Factures
│   └── Rapports
│
└── RH
    ├── Procédures
    └── Documents internes
```

Créer suffisamment de données pour que l'interface semble réelle.

---

## 7. Layout principal

Créer un layout desktop professionnel :

```
┌──────────────────────────────────────────────────────────┐
│ MesDocuments                  Recherche      Profil       │
├────────────────┬─────────────────────────────────────────┤
│                │                                         │
│ Mes documents  │                                         │
│ Partagés       │             Contenu                     │
│ Favoris        │                                         │
│ Récents        │                                         │
│ Corbeille      │                                         │
│                │                                         │
└────────────────┴─────────────────────────────────────────┘
```

Utiliser DSFR.

La navigation doit être claire et sobre.

---

## 8. Routes frontend

Créer au minimum :

- /
- /documents
- /documents/:folderId
- /files/:fileId
- /search
- /assistant
- /shared
- /favorites
- /recent

Les routes doivent être réellement navigables.

---

## 9. Page principale

Créer une page "Mes documents".

Afficher :

- breadcrumb ;
- nom du dossier courant ;
- bouton Nouveau ;
- bouton Importer ;
- recherche ;
- liste des fichiers/dossiers ;
- tri ;
- actions.

Exemple :

```
Mes documents

Accueil / Clients / ACME

[ + Nouveau ] [ Importer ]

---

Nom                 Type       Modifié

Contrats            Dossier    Aujourd'hui
Réunions            Dossier    Hier
contrat-2024.pdf    PDF        25 août
reunion.mp4         Vidéo      24 août
reunion.mp3         Audio      24 août
```

---

## 10. Navigation dossiers

Pouvoir :

- entrer dans un dossier ;
- revenir avec breadcrumb ;
- afficher les sous-dossiers ;
- afficher les fichiers ;
- revenir au dossier parent.

Le changement de dossier doit modifier la route.

---

## 11. Actions

Pour les fichiers :

- ouvrir ;
- télécharger ;
- renommer ;
- déplacer ;
- partager ;
- favoris ;
- détails ;
- versions ;
- supprimer.

Pour les dossiers :

- ouvrir ;
- renommer ;
- partager ;
- créer un sous-dossier ;
- supprimer.

Tout est mocké.

---

## 12. Création de dossier

Créer une vraie modal DSFR :

```
"Nouveau dossier"

Nom :

[________________]

[Annuler] [Créer]
```

Après création, le dossier doit apparaître dans l'interface mock.

---

## 13. Upload

Créer une vraie UX d'import.

```
Zone :

Déposez vos fichiers ici

ou

[ Choisir des fichiers ]

Afficher les fichiers :

contrat.pdf       2.4 Mo       70%
reunion.mp4       180 Mo       30%
```

États :

- sélectionné ;
- upload ;
- terminé ;
- erreur ;
- analyse en cours.

Même si tout est simulé.

Après l'import, simuler :

```
Upload terminé

puis :

Analyse du document

Texte extrait
Résumé généré
Indexation terminée
```

---

## 14. Page fichier

Créer une page détaillée.

Exemple :

```
← Clients / ACME / Contrats

Contrat ACME.pdf

PDF · 2.4 Mo

[ Télécharger ] [ Partager ] [ ... ]

Tabs :

Aperçu
Résumé
Informations
Versions
Activité
```

Afficher un aperçu du document.

---

## 15. Viewer PDF mock

Créer un faux viewer PDF suffisamment réaliste.

Afficher :

- numéro de page ;
- navigation page précédente/suivante ;
- zoom mock ;
- document ;
- zone surlignée.

Prévoir une fonction frontend :

```ts
openPdfAt({
  page: 12,
  bbox: [x0, y0, x1, y1]
})
```

Le mock doit simuler le déplacement vers la bonne page et le surlignage.

---

## 16. Audio

Créer un lecteur audio mock.

```
Réunion février.mp3

▶ ━━━━━━━━━●──────────

12:32 / 45:12

Transcription :

12:32 Alice
...

13:04 Bob
...
```

Lorsqu'une source est sélectionnée :

"Voir la source"

→ positionner le player au timestamp correspondant.

---

## 17. Vidéo

Créer un player vidéo mock.

```
┌──────────────────────────────┐
│                              │
│            VIDEO             │
│                              │
└──────────────────────────────┘

▶ ━━━━━━━━━●──────────────

12:32 / 54:12

Transcription.
```

Une source peut pointer vers :

- startMs
- endMs

Le mock doit pouvoir simuler le déplacement vers le timestamp.

---

## 18. Recherche

Créer une vraie page de recherche.

```
Champ :

[ Quels documents parlent de résiliation ? ]

Filtres :

- emplacement ;
- type ;
- date ;
- propriétaire ;
- dossier.

Résultats :

contrat-acme.pdf
PDF
Page 12

"... clause de résiliation ..."

contrat-total.pdf
PDF
Page 8

"... résiliation anticipée ..."
```

---

## 19. Recherche sémantique + keyword

Le frontend doit être capable de représenter :

- résultat keyword ;
- résultat sémantique ;
- résultat hybride.

Ne pas exposer la complexité technique par défaut.

Utiliser :

```ts
SearchResult {
  fileId: string
  fileName: string
  chunkId: string
  excerpt: string
  score: number
  source: DocumentSource
}
```

---

## 20. Question sur un fichier

Sur la page d'un fichier :

```
"Poser une question sur ce document"

[ Votre question... ]

[ Demander ]

Exemple :

Question :

"Quelle est la durée du contrat ?"

Réponse :

"Le contrat est conclu pour une durée initiale de trois ans."

Sources :

contrat-acme.pdf
Page 4

[ Voir la source ]
```

Cliquer sur "Voir la source" doit ouvrir le viewer sur la bonne page.

---

## 21. Question sur un dossier

Sur la page d'un dossier :

```
"Poser une question sur ce dossier"

[ Votre question... ]

Option :

☑ Inclure les sous-dossiers

Exemple :

"Quels contrats arrivent à échéance cette année ?"
```

Afficher une réponse avec plusieurs sources.

---

## 22. Scope

Le frontend doit toujours montrer le scope de la recherche.

```
Recherche dans :

[ Clients / ACME ]

☑ Inclure les sous-dossiers

Pour une recherche globale :

Recherche dans :

[ Tous mes documents ]
```

Le scope doit faire partie des modèles frontend :

```ts
type QueryScope = {
  type: "file" | "folder" | "all"
  id?: string
  recursive?: boolean
}
```

---

## 23. Sources

Créer un composant :

`DocumentSources`

Il doit afficher :

```
Pour PDF :

contrat.pdf — page 12

Pour audio :

reunion.mp3 — 12:32 → 13:05

Pour vidéo :

reunion.mp4 — 12:32 → 13:05
```

Prévoir :

```ts
type DocumentSource =
  | {
      type: "pdf"
      fileId: string
      page: number
      bbox?: [number, number, number, number]
    }
  | {
      type: "audio"
      fileId: string
      startMs: number
      endMs: number
    }
  | {
      type: "video"
      fileId: string
      startMs: number
      endMs: number
    }
```

---

## 24. Partage

Créer une modal :

```
Partager "contrat-acme.pdf"

Personnes ayant accès :

Alice Dupont       Éditeur
Bob Martin         Lecteur
Groupe Finance     Lecteur

[ Ajouter ]

Ajouter :

Utilisateur ou groupe
[________________]

Permission :

○ Lecteur
○ Éditeur

[ Ajouter ]
```

Tout est mocké.

---

## 25. Permissions

Afficher clairement :

- Accès direct
- Accès hérité
- Accès refusé

Exemple :

```
Dossier :
Alice → Lecteur

Fichier :
Alice → Accès refusé
```

Ne jamais implémenter la logique réelle de permission côté frontend.

Le frontend affiche simplement l'état mock fourni par le repository.

---

## 26. Agent MesDocuments

Créer une page :

`/assistant`

```
Titre :

MesDocuments Assistant

Description :

"Je peux rechercher, parcourir et analyser les documents auxquels vous avez accès."
```

Interface conversationnelle.

Exemple :

```
Utilisateur :

"Trouve les contrats ACME et compare leurs conditions de résiliation."

Agent :

Recherche dans Clients / ACME...

✓ 12 documents trouvés
✓ 4 contrats identifiés
✓ Analyse des clauses de résiliation
✓ Vérification des sources

Puis :

"J'ai identifié 4 contrats..."

Sources :

contrat-2024.pdf — p.12
avenant-2025.pdf — p.4
...
```

---

## 27. Activité de l'agent

Créer :

`AgentActivity`

Afficher des étapes compréhensibles.

Exemple :

```
✓ Recherche dans "Clients / ACME"
✓ 18 documents trouvés
✓ Analyse de 6 documents
⏳ Comparaison des clauses
```

NE PAS afficher de chain-of-thought.

Ne jamais afficher les raisonnements internes du modèle.

Afficher uniquement des statuts d'activité utiles à l'utilisateur.

---

## 28. Agent contextuel

Depuis un dossier :

```
[ Assistant ]

L'agent reçoit automatiquement :

{
  type: "folder",
  id: "...",
  recursive: true
}
```

Depuis un fichier :

```ts
{
  type: "file",
  id: "..."
}
```

Le frontend doit représenter ce contexte dans l'interface.

---

## 29. Pages supplémentaires

Créer :

- /shared
- /favorites
- /recent

avec de vraies données mockées.

---

## 30. États UI

Chaque écran doit gérer :

- loading ;
- empty ;
- error ;
- forbidden ;
- not found ;
- processing.

Exemple :

```
"Aucun document"

"Ce dossier ne contient encore aucun document."

[ Importer un document ]
```

---

## 31. Responsive

Supporter :

- desktop ;
- tablette ;
- mobile.

Le desktop est prioritaire.

Sur mobile :

- navigation adaptée ;
- liste de fichiers adaptée ;
- assistant utilisable ;
- modales adaptées.

---

## 32. Accessibilité

Respecter :

- navigation clavier ;
- focus ;
- labels ;
- messages d'erreur ;
- structure HTML ;
- contraste ;
- attributs ARIA si nécessaires.

Utiliser les composants DSFR correctement.

---

## 33. Design

Le design doit être :

- professionnel ;
- sobre ;
- clair ;
- orienté productivité ;
- cohérent avec DSFR ;
- peu chargé ;
- lisible avec beaucoup de documents.

Ne pas chercher à créer un design "futuriste IA".

L'IA doit être intégrée naturellement dans le gestionnaire documentaire.

---

## 34. Priorité UX

Les parcours les plus importants sont :

### Parcours 1

Mes documents → dossier → sous-dossier → fichier → aperçu

### Parcours 2

Fichier → question → réponse → source → page PDF / timestamp

### Parcours 3

Dossier → question → recherche récursive → plusieurs documents → sources

### Parcours 4

Fichier → partager → utilisateur/groupe → permission

### Parcours 5

Assistant → tâche complexe → recherche → activité → réponse → sources

Ces parcours doivent être particulièrement bien travaillés.

---

## 35. Ne pas faire

NE PAS :

- créer le backend ;
- créer des endpoints ;
- installer FastAPI ;
- configurer Keycloak ;
- configurer Qdrant ;
- configurer OpenSearch ;
- créer PostgreSQL ;
- créer une queue ;
- créer des workers ;
- intégrer un vrai LLM ;
- intégrer MCP ;
- intégrer A2A ;
- faire du chiffrement backend.

Cette phase est 100 % frontend.

---

## 36. Commencer par l'expérience

Avant de générer beaucoup de code :

1. analyser le besoin ;
2. définir les parcours ;
3. définir les routes ;
4. définir les composants ;
5. définir les types TypeScript ;
6. définir les mocks ;
7. construire le layout ;
8. construire les pages ;
9. construire les interactions ;
10. vérifier la cohérence UX.

Ne pas sur-architecturer.

---

## 37. Critère de réussite

À la fin, je veux pouvoir lancer :

```bash
npm install
npm run dev
```

et utiliser MesDocuments comme une vraie application :

- naviguer dans les dossiers ;
- ouvrir des fichiers ;
- simuler des uploads ;
- rechercher ;
- poser des questions ;
- voir les sources ;
- naviguer vers une page PDF ;
- naviguer vers un timestamp audio/vidéo ;
- partager ;
- voir les permissions ;
- utiliser l'agent.

Tout fonctionne avec des données mockées.

Le résultat doit être suffisamment abouti pour que je puisse tester l'UX avec de vrais utilisateurs AVANT de commencer le backend.

---

## 38. Règle fondamentale

Ne construis pas le backend "en avance".

Le frontend doit être considéré comme un produit indépendant utilisant actuellement un "Mock Document Service".

Plus tard seulement, nous remplacerons :

- MockDocumentRepository
- MockSearchRepository
- MockAgentRepository
- MockPermissionRepository

par des repositories connectés à l'API backend.

Commence maintenant par le frontend uniquement.

---

Le plan d'exécution détaillé (phases et TODO) est suivi séparément dans [FRONTEND_TODO.md](./FRONTEND_TODO.md).
