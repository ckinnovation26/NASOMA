# CLAUDE.md — Contexte projet NASOMA

> **À LIRE EN PREMIER par toute instance Claude (chat, Claude Code local, agent) avant toute action sur ce repo.**
> Dernière mise à jour : 22 mai 2026 — Version 1.0

---

## 0. Identité du projet

- **Nom de la marque** : Nasoma (du swahili « ni-na-soma » = « moi, j'étudie »)
- **Slogan** : *« Mimi, Nasoma. »*
- **Pitch** : *« Nasoma tue la lacune dans l'œuf, jour après jour, devoir après devoir. »*
- **Société** : CK Innovation SARL (Moroni, Union des Comores)
- **Fondateur / dev principal** : ABDU LKADER Mohamed Amound (Kader) — kader@ckinnovation.fr
- **Repo** : github.com/ckinnovation26/NASOMA (privé)
- **Statut** : MVP en développement actif (Q3 2026)
- **Filiation** : Projet LISEC (2018) → Projet SOMA (2024) → Nasoma (2026)

---

## 1. Vision & workflow cœur (NE PAS DÉVIER DE ÇA)

### Vision
> Faire en sorte qu'aucun élève africain ne termine sa journée scolaire sur une incompréhension non traitée.

### Le workflow « Scan-Rattrapage »
```
[Devoir corrigé en classe]
  → [Scan smartphone par l'élève ou le parent]
  → [IA Vision : extraction erreurs + annotations professeur + ratures]
  → [Diagnostic : localisation précise de la rupture de logique]
  → [Pack remédiation flash : 3-4 micro-exercices ciblés]
  → [Mise à jour Knowledge Graph de l'élève (BKT)]
```

### Différenciation marché
- **Préventif, pas curatif** : agit le soir même, pas 2 semaines avant l'examen
- **Aligné sur les curriculums nationaux africains** (APC Comores, CBC Kenya, NECTA Tanzanie) — pas Khan Academy hors-curriculum
- **Frugal** : Android entrée de gamme, offline-first, 2G/3G
- **Marché pilote** : Union des Comores (réseau institutionnel CK Innovation depuis 2018)

---

## 2. Stack technique

```
┌─────────────────────────────────────────────────────┐
│  App mobile : Flutter (Dart)                         │
│  ├── ML Kit Text Recognition (OCR on-device)        │
│  ├── Riverpod (state management)                    │
│  ├── go_router (navigation)                         │
│  ├── Drift (SQLite offline)                         │
│  └── Firebase Auth (OTP SMS/WhatsApp)               │
└──────────────────┬──────────────────────────────────┘
                   │ HTTPS TLS 1.3
                   ▼
┌─────────────────────────────────────────────────────┐
│  Backend : Google Cloud Run (africa-south1)          │
│  ├── FastAPI (Python 3.12)                          │
│  ├── PostgreSQL via Cloud SQL (BKT, analytics)      │
│  ├── Firestore (quotas, cache scan, sessions live)  │
│  ├── Cloud Storage (scans, TTL 30j)                 │
│  └── Cloud Tasks (pipeline OCR async)               │
└──────────────────┬──────────────────────────────────┘
                   │ Pipeline OCR 3 étages
                   ▼
┌─────────────────────────────────────────────────────┐
│  IA Cloud (fallback si ML Kit confidence < 85%)      │
│  ├── Google Cloud Vision API  (~$0.0015/page)       │
│  └── Gemini 2.0 Flash (cas difficiles)              │
│                                                      │
│  SMS/Paiement : Africa's Talking + Hollo Money      │
│  (Comores) + Mvola + Stripe (diaspora)              │
└─────────────────────────────────────────────────────┘
```

### Pipeline OCR (algorithme cible)
1. **ML Kit on-device** → si confidence > 85 % : traitement direct, fin
2. **Cloud Vision API** → si confidence entre 70 % et 85 %
3. **Gemini 2.0 Flash** → si confidence < 70 %
4. **Fallback "Always Give Value"** → si Gemini < seuil minimal

> **Cible** : 90 % des cas traités sans Cloud Vision ni Gemini.

### Coût d'exploitation estimé
| Poste | Coût mensuel |
|---|---|
| Cloud Run (scale-to-zero) | ~0-5 $ |
| Cloud SQL (db-f1-micro) | ~7 $ |
| Firebase Auth | Gratuit |
| Firestore | ~0-2 $ (free tier) |
| Cloud Vision API | ~1-3 $/1000 scans |
| Gemini 2.0 Flash | ~0.04-0.075 $/1M tokens |
| Africa's Talking SMS | ~0.02 $/SMS |
| **TOTAL fixe MVP** | **~10-15 $/mois** |

---

## 3. Modèle économique

### Pricing (verrouillé)
| Plan | Prix | Inclus |
|---|---|---|
| **Découverte** | Gratuit | 3 scans / 7 jours, 1 profil élève |
| **Pro** | 2 000 KMF/mois (~4 €) | Scans illimités, jusqu'à 4 profils, rapports SMS parents |
| **Famille** | 3 500 KMF/mois (~7 €) | 4 profils, toutes matières, historique 1 an |
| **École** (V1.2+) | Sur devis | Tableau de bord directeur, export PDF notes |

### Paiement (marché Comores)
- **Hollo Money** (Comores) — intégration prioritaire
- **Mvola** (Madagascar) — vague 2
- **Stripe** — diaspora / cartes bancaires
- **Codes de recharge physiques** `NSMA-XXXX-XXXX-XXXX` — vendeurs locaux (boutiques, épiceries)

### Grace period
- 30 jours en lecture seule après expiration — l'élève voit ses anciens diagnostics mais ne peut plus scanner

---

## 4. Scope MVP V1.0 (le seul scope qui compte aujourd'hui)

### ✅ Inclus dans V1.0
- Scan devoir corrigé (caméra Android)
- OCR 3 étages (ML Kit → Cloud Vision → Gemini)
- Diagnostic IA : extraction erreurs, localisation lacune, mise à jour Knowledge Graph
- Pack remédiation flash : 3-4 micro-exercices générés par Gemini Flash
- Profil élève (Knowledge Graph BKT par concept)
- Authentification OTP SMS (Africa's Talking) + fallback WhatsApp
- Plan Découverte (3 scans gratuits) + paywall soft
- Curriculum : mathématiques + français 6e (Comores APC)
- Langue UI : Swahili + Arabe + Shimori (shk)
- Mode hors-ligne partiel (Drift SQLite, sync à la reconnexion)
- Rapports SMS parents (résumé hebdomadaire)
- Android uniquement

### ❌ Exclus V1.0 (backlog post-V1)
- iOS
- Paiement intégré en ligne (Sprint suivant)
- Tableau de bord école/directeur
- Audio / vidéo (V2)
- Autres pays (Kenya, Tanzanie) — Vague 2
- Curriculums autres niveaux (5e, 4e, lycée)
- Reconnaissance vocale
- Mode multijoueur / gamification sociale

### Règle d'or
> **Si une fonctionnalité n'est pas dans la liste "✅ Inclus" ci-dessus, elle va dans le backlog. Pas dans le code V1.0.**

---

## 5. Identité visuelle & design

### Marque
- **Palette** : Fond noir `#000000`, accent lime `#D4FF80`, texte `#F5F5F5`
- **Ton** : Puissant et bienveillant — « tuteur de quartier qui connaît le curriculum local »
- **Mascotte** : Mimi (personnage symbolisant l'élève africain qui réussit)
- **Dark mode** obligatoire dès V1.0

### Design tokens (déjà dans `app_theme.dart`)
```dart
black      = Color(0xFF000000)   // Fond principal
charcoal   = Color(0xFF1A1A1A)   // Fond secondaire / inputs
limeAccent = Color(0xFFD4FF80)   // CTA principal, succès
textPrimary   = Color(0xFFF5F5F5)
textSecondary = Color(0xFFB0B0B0)
textTertiary  = Color(0xFF6B6B6B)
borderSubtle  = Color(0xFF2A2A2A)
warning = Color(0xFFFFB84A)
error   = Color(0xFFFF6B6B)
```

### Conventions UI
- Typographie : **Inter** (Google Fonts)
- Border radius boutons : 16 px
- Border radius inputs : 12 px
- Taille minimale bouton principal : 56 px hauteur, pleine largeur
- Animations : ease-out, 200-350 ms

---

## 6. Conventions de code

### Python / FastAPI (backend)
- **Python 3.12 strict** — mypy strict activé, pas de `Any` sauf justification
- **Ruff** linter + formatter (line-length 100)
- **SQLAlchemy 2.0 async** uniquement (pas de sync)
- **Pydantic v2** pour tous les schémas
- Structlog pour tous les logs (pas de `print`, pas de `logging` standard)
- Naming :
  - Modules : `snake_case`
  - Classes : `PascalCase`
  - Constantes : `SCREAMING_SNAKE_CASE`
  - Fonctions/variables : `snake_case`
- Tout nouveau service dans `app/services/`, tout nouveau modèle dans `app/models/`
- Tout endpoint dans `app/api/v1/` avec son propre fichier router

### Dart / Flutter (mobile)
- **Dart null-safety strict** — pas de `!` sauf justification commentée
- **Riverpod** pour tout état — pas de setState sauf widgets purement locaux
- **go_router** pour toute navigation
- Naming :
  - Fichiers : `snake_case.dart`
  - Classes/Widgets : `PascalCase`
  - Providers : `camelCaseProvider`
  - Constantes : `camelCase` dans une classe statique
- Structure features-first : `lib/features/<feature>/presentation/`, `data/`, `domain/`
- Un screen = un fichier dans `presentation/`
- Un provider = un fichier dans `data/` ou `domain/`
- Jamais de logique métier dans un Widget — extraire dans un provider ou un service

### Structure de dossiers cible (backend)
```
backend/app/
├── api/v1/          ← 1 fichier = 1 domaine (auth.py, scans.py...)
├── core/            ← config, logging, security
├── db/              ← session SQLAlchemy, client Firestore
├── models/          ← modèles SQLAlchemy ORM
├── schemas/         ← schémas Pydantic (request/response)
├── services/        ← logique métier pure
│   └── payments/    ← providers paiement (hollo, mvola, stripe)
└── workers/         ← handlers Cloud Tasks
```

### Structure de dossiers cible (mobile)
```
mobile/lib/
├── core/
│   ├── api/         ← client HTTP + repositories abstraits
│   ├── constants/   ← AppConstants
│   ├── env/         ← dart-define
│   ├── router/      ← app_router.dart (go_router)
│   └── theme/       ← app_theme.dart
└── features/
    ├── auth/
    │   ├── data/    ← auth_repository_impl.dart, providers
    │   ├── domain/  ← modèles locaux, interfaces
    │   └── presentation/ ← screens
    ├── scan/        ← même structure
    ├── session/     ← même structure
    ├── home/
    ├── onboarding/
    └── splash/
```

### Tests
- **Backend** : pytest + pytest-asyncio, couverture cible 80 % sur `services/` et `core/`
- **Mobile** : flutter_test + mocktail, tests unitaires providers obligatoires
- Pas de test sur les Workers Cloud Tasks en V1.0 (trop lourds)

### Git
- Branches : `main` (prod), `develop` (intégration), `feat/xxx`, `fix/xxx`, `chore/xxx`
- Commits : Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:`)
- Pas de commit direct sur `main`
- Avant chaque commit backend : `ruff check . && mypy app/`
- Avant chaque commit mobile : `flutter analyze && flutter test`

---

## 7. Définition du « Done »

Une tâche est **Done** UNIQUEMENT si TOUTES ces cases sont cochées :

- [ ] Code commité sur `develop` avec message Conventional Commits clair
- [ ] Build backend OK (`uvicorn app.main:app --reload` sans erreur)
- [ ] Build mobile OK (`flutter run -d chrome` ou APK debug sans crash)
- [ ] TypeScript / mypy / ruff passent sans erreur
- [ ] `flutter analyze` passe sans warning
- [ ] Si feature backend → au moins 1 test unitaire ajouté
- [ ] `AUDIT_22mai2026.md` mis à jour (tâche cochée ✅, changelog mis à jour)

---

## 8. Roadmap Q3 2026

| Sprint | Période | Objectif |
|---|---|---|
| Sprint 1 | Juin 2026 | Débloquants : migrations, auth OTP, pipeline OCR, APK debug |
| Sprint 2 | Juillet 2026 | Flow complet : Scan → Diagnostic → Session → BKT |
| Sprint 3 | Août 2026 | Bêta-test 30 élèves Comores + paiement Hollo Money |

### OKR Q3 2026
- **O1** — APK Android testable par 30 élèves comoriens ≤ 31 juillet
- **O2** — 5 familles pilotes payantes (Hollo Money) ≤ 31 août
- **O3** — NPS ≥ 35 après 4 semaines d'usage réel

---

## 9. Ce que Claude Code DOIT faire avant chaque action

### À chaque session
1. Lire ce CLAUDE.md en entier
2. Lire `AUDIT_22mai2026.md` pour connaître l'état exact des tâches
3. Vérifier que la tâche demandée entre dans le scope V1.0 (section 4)
4. Si hors scope → NE PAS implémenter, signaler à Kader et ajouter au backlog

### Avant d'écrire du code
1. Vérifier les conventions (section 6)
2. Vérifier la structure de dossiers cible (section 6)
3. Vérifier les design tokens (section 5) pour tout composant Flutter

### Après chaque tâche complétée
1. Mettre à jour `AUDIT_22mai2026.md` : cocher la tâche ✅, ajouter une ligne dans le changelog
2. Vérifier chaque case de la définition du Done (section 7)
3. Signaler explicitement à Kader ce qui n'a pas pu être coché

### Décisions stratégiques
- Claude Code NE prend PAS de décisions stratégiques seul
- Claude Code peut PROPOSER, Kader valide
- Toute décision = écrite, datée, signée dans ce CLAUDE.md

---

## 10. Liens & ressources

- **GitHub repo** : github.com/ckinnovation26/NASOMA (privé)
- **Hetzner / GCP Console** : console.cloud.google.com (projet `nasoma-prod`)
- **Firebase Console** : console.firebase.google.com (projet `nasoma-dev` / `nasoma-prod`)
- **Google Play Console** : play.google.com/console (compte 3333636km@gmail.com)
- **Africa's Talking** : africastalking.com/dashboard
- **Audit vivant** : `AUDIT_22mai2026.md` (ce dossier)
- **Business Plan complet** : `NASOMA_Business_Plan_et_Cahiers_des_Charges.md`

---

## 11. Garde-fous absolus

🚫 **Anti-dispersion**
- Aucune fonctionnalité hors scope V1.0 avant 30 élèves actifs testeurs
- Curriculum : Comores uniquement en V1.0 (pas Kenya, pas Tanzanie)
- Pas d'iOS, pas de web app standalone

🎯 **Discipline d'exécution**
- Si le flow Scan → Diagnostic → Session ne marche pas parfaitement → on ne passe pas à la suite
- Priorité absolue : le scan fonctionne sur un vrai devoir comorien

💡 **Principe Pareto**
- 80 % du temps sur : **scan + diagnostic IA + micro-exercices**
- Le reste = backlog

---

## 12. Ce document est vivant

Mettre à jour ce CLAUDE.md :
- À chaque changement de stack
- À chaque évolution du scope V1.0
- À chaque sprint review

**Ne JAMAIS supprimer une section sans validation explicite de Kader.**

---

*Document créé le 22 mai 2026 — Version 1.0*
*CK Innovation SARL — ABDU LKADER Mohamed Amound*
*kader@ckinnovation.fr — Moroni, Union des Comores*

> **Ce fichier est la source de vérité du projet NASOMA.**
> *Toute incohérence entre le code et ce fichier doit être signalée immédiatement à Kader.*
