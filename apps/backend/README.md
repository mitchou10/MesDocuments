# MesDocuments — Backend

Étape actuelle : **authentification uniquement**, via un pattern **BFF
(Backend For Frontend)**. L'API FastAPI ne fait rien d'autre pour l'instant
que gérer le login OAuth avec Keycloak et exposer l'identité de l'utilisateur
courant via une session cookie. Pas de documents, pas de base de données, pas
de PostgreSQL — ça viendra dans une prochaine étape.

## Pourquoi un BFF plutôt qu'un login direct SPA → Keycloak ?

Le frontend ne parle jamais directement à Keycloak et ne voit jamais de JWT :
c'est le backend qui échange le code OAuth (PKCE) contre les tokens, côté
serveur, et qui pose un cookie de session `httpOnly`. Le token d'accès ne
transite donc jamais par le JavaScript du navigateur — moins de surface XSS
qu'un stockage en `localStorage`.

## Stack

- FastAPI + Uvicorn
- `httpx` pour les appels serveur-à-serveur à Keycloak (échange de code, refresh)
- PyJWT pour vérifier les tokens reçus de Keycloak (RS256, clés JWKS)
- Keycloak comme fournisseur d'identité (OIDC, client confidentiel)
- `uv` pour la gestion des dépendances Python

## Lancer en local

```bash
uv sync
uv run uvicorn app.main:app --reload
```

## Lancer avec Docker (Keycloak + frontend inclus)

Depuis la racine du repo :

```bash
docker compose up
# ou avec hot-reload sur les changements de code :
docker compose watch
```

- Frontend : http://localhost:5173 (proxie `/api/*` vers le backend — voir
  `apps/frontend/vite.config.ts` — pour que le cookie de session reste
  same-site du point de vue du navigateur)
- Backend : http://localhost:8000 (ou via le proxy : http://localhost:5173/api/...)
- Keycloak : http://localhost:8080 (admin console : `admin` / `admin`)
- Realm pré-importé : `mesdocuments` (voir `../../infra/keycloak/realm-export.json`)
- Utilisateur de test : `camille.bernard` / `camille`

## Endpoints

| Méthode | Route                     | Auth requise | Description |
|---------|---------------------------|--------------|--------------|
| GET     | `/health`                 | non          | Liveness check |
| GET     | `/api/v1/auth/login`      | non          | Démarre le login (redirige vers Keycloak, PKCE) |
| GET     | `/api/v1/auth/callback`   | non          | Callback OAuth : échange le code, crée la session, pose le cookie |
| GET     | `/api/v1/auth/me`         | oui (cookie) | Identité + rôles de l'utilisateur courant |
| GET     | `/api/v1/auth/logout`     | non          | Efface la session locale et termine la session SSO Keycloak |

## Configuration (variables d'environnement, préfixe `MESDOCUMENTS_`)

| Variable                     | Défaut                                                | Rôle |
|-------------------------------|--------------------------------------------------------|------|
| `KEYCLOAK_ISSUER`              | `http://localhost:8080/realms/mesdocuments`             | Doit correspondre exactement au claim `iss` des tokens ; aussi utilisé pour les URLs `/auth` et `/logout` que le navigateur suit |
| `KEYCLOAK_JWKS_BASE_URL`       | (vide → dérivé de `KEYCLOAK_ISSUER`)                    | Chemin réseau réel pour récupérer les clés JWKS (le backend peut joindre Keycloak via `keycloak:8080` en Docker alors que le navigateur, lui, utilise `localhost`) |
| `KEYCLOAK_TOKEN_BASE_URL`      | (vide → dérivé de `KEYCLOAK_ISSUER`)                    | Idem, pour l'échange de code et le refresh (appels serveur à serveur) |
| `KEYCLOAK_CLIENT_ID`           | `mesdocuments-backend`                                  | Client OAuth confidentiel utilisé par le backend |
| `KEYCLOAK_CLIENT_SECRET`       | `dev-secret-change-me`                                  | Secret du client (à changer hors dev !) |
| `KEYCLOAK_REDIRECT_URI`        | `http://localhost:5173/api/v1/auth/callback`            | URL de callback *publique* (vue par le navigateur, via le proxy du frontend) |
| `KEYCLOAK_AUDIENCE`            | `mesdocuments-backend`                                  | Audience attendue dans le token (`aud`) |
| `FRONTEND_BASE_URL`            | `http://localhost:5173`                                 | Où rediriger après login/logout |
| `SESSION_COOKIE_NAME`          | `mesdocuments_session`                                  | Nom du cookie de session |
| `SESSION_TTL_SECONDS`          | `28800` (8h)                                            | Durée de vie du cookie |
| `CORS_ORIGINS`                 | `["http://localhost:5173"]`                             | Origines autorisées |

## Comment ça marche

1. Le frontend redirige le navigateur vers `/api/v1/auth/login` (navigation
   complète, pas un appel `fetch`).
2. Le backend génère une paire PKCE (`code_verifier`/`code_challenge`), la
   garde en mémoire le temps du login, et redirige vers Keycloak.
3. L'utilisateur s'authentifie sur Keycloak (le backend ne voit jamais son
   mot de passe).
4. Keycloak redirige le navigateur vers `/api/v1/auth/callback?code=...` (via
   le proxy du frontend). Le backend échange ce code contre des tokens
   **côté serveur** (`code_verifier` inclus), vérifie l'`access_token` reçu
   (signature JWKS, issuer, audience), crée une session en mémoire et pose un
   cookie `httpOnly` — puis redirige vers la page d'origine du frontend.
5. Chaque appel protégé du frontend (`/api/v1/auth/me`, et plus tard les
   endpoints métier) envoie ce cookie automatiquement ; le backend retrouve
   la session et, si le token a expiré, le rafraîchit via le `refresh_token`
   avant de répondre.
6. `/api/v1/auth/logout` efface la session locale et redirige vers l'endpoint
   de logout de Keycloak (`id_token_hint` inclus) pour terminer aussi la
   session SSO.

⚠️ Le stockage de session est actuellement un simple dict en mémoire
(`app/services/sessions.py`) : parfait pour un seul process de dev, à remplacer
par Redis (ou équivalent partagé) avant tout déploiement multi-instance.

## Tests

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Les tests signent eux-mêmes des tokens avec une paire de clés RSA générée à la
volée et simulent l'échange de code (voir `tests/test_auth.py`) : aucun
Keycloak réel n'est nécessaire pour les faire tourner.

## Tester manuellement le flow complet (sans navigateur)

```bash
# 1. Démarrer Keycloak + backend + frontend (le proxy Vite est nécessaire)
docker compose up -d

# 2. Suivre la redirection de login avec un cookie jar
curl -c jar.txt -b jar.txt -L "http://localhost:5173/api/v1/auth/login?return_to=/documents" -o login.html

# 3. Extraire l'action du formulaire Keycloak dans login.html, puis :
curl -c jar.txt -b jar.txt -L \
  --data-urlencode "username=camille.bernard" \
  --data-urlencode "password=camille" \
  "<action extraite du formulaire>"

# 4. Vérifier la session
curl -b jar.txt http://localhost:5173/api/v1/auth/me
```

## Prochaines étapes (pas encore faites)

Construire les endpoints métier (dossiers, fichiers, recherche…) derrière
`get_current_user`, remplacer le stockage de session en mémoire par Redis, et
brancher le frontend (aujourd'hui toujours sur des données mockées) sur cette
vraie identité.
