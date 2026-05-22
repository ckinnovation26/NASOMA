# Nasoma — Architecture

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                     📱 Mobile (Flutter)                      │
│                                                              │
│  ML Kit ──┐                                                  │
│  Camera ──┼─► Preprocessing ──► API REST ──► UI Riverpod    │
│  Drift  ──┘                                                  │
└─────────────────────┬────────────────────────────────────────┘
                      │ HTTPS TLS 1.3
                      ▼
┌─────────────────────────────────────────────────────────────┐
│            🌍 Google Cloud (africa-south1)                   │
│                                                              │
│  ┌─────────────┐    ┌─────────────────────────────────┐    │
│  │ Cloud Run   │───►│ Firestore (quotas, cache scan)  │    │
│  │ FastAPI     │    └─────────────────────────────────┘    │
│  │             │    ┌─────────────────────────────────┐    │
│  │             │───►│ Cloud SQL Postgres (BI, BKT)    │    │
│  │             │    └─────────────────────────────────┘    │
│  │             │    ┌─────────────────────────────────┐    │
│  │             │───►│ Cloud Storage (scans, TTL 30j)  │    │
│  │             │    └─────────────────────────────────┘    │
│  │             │    ┌─────────────────────────────────┐    │
│  │             │───►│ Cloud Tasks ──► OCR Worker      │    │
│  └─────────────┘    └─────────┬───────────────────────┘    │
│                                │                            │
│                                ▼                            │
│                    ┌──────────────────────┐                 │
│                    │ Vision API           │ ~1.5$/1k pages │
│                    │ Gemini 2.0 Flash     │ ~0.075$/1M tok │
│                    │ Gemini 1.5 Flash-8B  │ ~0.04$/1M tok  │
│                    └──────────────────────┘                 │
│                                                              │
│  ┌──────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │ Firebase     │  │ FCM Push    │  │ Cloud Logging   │    │
│  │ Auth (OTP)   │  │             │  │ + BigQuery      │    │
│  └──────────────┘  └─────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘

External:
  • Africa's Talking (SMS rapports parents)
  • Hollo Money + Mvola + M-Pesa (paiement)
```

## Décisions clés

### Pourquoi GCP + Firebase plutôt que AWS ?
- **Coût** : Firebase Auth gratuit, Firestore free tier généreux, Cloud Run scale-to-zero.
- **Région** : `africa-south1` (Johannesburg) plus proche des Comores que AWS Cape Town.
- **Stack ML** : Vision API, Gemini, ML Kit Flutter — tout du même fournisseur.
- **Cohérence Flutter ↔ Firebase** : SDK officiels, code-gen propre.

### Pourquoi Firestore + Postgres (et pas un seul) ?
- **Firestore** : écritures temps réel, scale-to-zero, parfait pour les quotas (transactions atomiques), le cache scan, les sessions chaudes.
- **Postgres** : modèle relationnel pour le knowledge graph DAG, les analytics BKT, les requêtes complexes (jointures écoles ↔ classes ↔ élèves).
- Pas de duplication : chaque donnée a UN owner.

### Pourquoi Gemini Flash-8B et pas Claude Haiku ?
- **20× moins cher** ($0.04 vs $0.80 par 1M tokens input)
- **JSON Mode natif** avec `responseSchema` (anti-hallucination)
- **Context Caching** : le knowledge graph (~50k tokens) est mis en cache → -75 % sur les calls suivants
- **Vision intégrée** : pas besoin de pipeline séparé

## Pipeline OCR — 3 étages

```
┌─────────────────────────────────────────────────────────┐
│  1. ML Kit on-device (gratuit)                          │
│     Confiance > 85% ? ──► STOP                          │
└─────────────┬───────────────────────────────────────────┘
              │ sinon
              ▼
┌─────────────────────────────────────────────────────────┐
│  2. Cloud Vision Document Text Detection (1.5$/1k pg)   │
│     Confiance > 70% ? ──► STOP                          │
└─────────────┬───────────────────────────────────────────┘
              │ sinon (cas vraiment difficiles)
              ▼
┌─────────────────────────────────────────────────────────┐
│  3. Gemini 2.0 Flash Vision (image directe)             │
│     Toujours réussi ou flagged human-review             │
└─────────────────────────────────────────────────────────┘
```

Cible : 60 % cas étage 1, 35 % étage 2, 5 % étage 3 → coût moyen **~0,001 $/scan**.

## Anti-hallucination

1. **Grounding obligatoire** : le curriculum (~650 concepts JSON) est passé en contexte à chaque call via Gemini Context Caching.
2. **Structured Output** : `responseSchema` JSON imposé, refus si non-conformité.
3. **Temperature** : 0.0 pour extraction/mapping, 0.2 pour génération.
4. **Validation post-LLM** : `concept_code` rejeté s'il n'existe pas dans le KG local.
5. **Safety Filters** : Vertex AI BLOCK_MEDIUM_AND_ABOVE sur toutes les générations enfant.

## Flux de scan complet

```
Élève              Mobile              Backend           Worker         Firestore
  │                  │                   │                 │                │
  ├─ tap camera ────►│                   │                 │                │
  │                  ├─ check quota ────►│                 │                │
  │                  │◄── ok, 2 left ────┤                 │                │
  ├─ shoot ─────────►│                   │                 │                │
  │                  ├─ compress 1024,75 │                 │                │
  │                  ├─ ML Kit local     │                 │                │
  │                  ├─ pHash            │                 │                │
  │                  ├─ POST /scans ────►│                 │                │
  │                  │                   ├─ check pHash ──►│ cache miss     │
  │                  │                   ├─ enqueue task ─►│                │
  │                  │◄── scan_id, 202 ──┤                 │                │
  │                  │                   │                 ├─ Cloud Vision  │
  │                  │                   │                 ├─ Gemini map    │
  │                  │                   │                 ├─ Gemini exos   │
  │                  │                   │                 ├─ save Postgres │
  │                  │                   │                 ├─ decrement ───►│
  │                  │ ◄── push FCM ─────┤◄── done ────────┤                │
  │ ◄── voir diag ───┤                   │                 │                │
```

## Choix de modélisation

### Knowledge Graph (DAG)
- Nœuds : `concepts` (table Postgres)
- Arêtes : `concept_prerequisites` (table de jointure many-to-many)
- Pas de cycle (vérifié par `pedagogy/scripts/validate_concepts.py`)

### BKT — Bayesian Knowledge Tracing
- Table `student_concept_mastery` : `(student_id, concept_id, mastery_prob, last_seen)`
- Mise à jour à chaque `session_answer`
- Paramètres standards : `p_init=0.1, p_transit=0.2, p_slip=0.1, p_guess=0.25`

### Quotas (Firestore)
- Collection `user_quotas/{user_id}` : `{ remaining, plan, expires_at, family_id }`
- Décrément via **transaction Firestore** (jamais en SQL — concurrent write protection)

## Scalabilité

### Y1 (500 users pilote)
- Cloud Run min=0 max=2, db-f1-micro, ~10 $/mois
- Aucune optimisation prématurée nécessaire

### Y2 (50 000 users)
- Cloud Run min=2 max=20, db-custom-2-7680, ~250 $/mois
- Migration BigQuery pour analytics historiques
- Sharding Firestore par tenant si > 1M writes/jour

### Y3 (500 000 users)
- Multi-régions (Lagos, Nairobi) si latence
- Read replicas Postgres
- CDN images statique

## Sécurité

→ Voir [`security.md`](security.md).

## Authentification & cycle de vie du compte

> Cf. [`strategie_Nasoma.md`](strategie_Nasoma.md) section 3 quater pour le rationale stratégique.

### OTP 3-en-1
Un OTP Nasoma sert simultanément à :
1. **Authentifier** l'utilisateur (mot de passe associé au phone identifiant)
2. **Prouver le paiement** d'un service (montant + plan)
3. **Ouvrir une session de crédit** (durée définie : 24h / 7j / 30j)

### Cycle de vie compte

```
inscription SMS → ACTIF → (crédit expire) → GRACE 30j → GELÉ → (J+365) → ARCHIVÉ
                    ↑                          ↓
                    └─── nouveau ticket ───────┘
```

| État | Login | Lecture données | Nouvelles actions | Durée |
|---|---|---|---|---|
| **ACTIF** | phone + OTP courant | ✅ | ✅ | tant que crédit > 0 ou expires_at > NOW |
| **GRACE** | phone + dernier OTP valide | ✅ lecture seule | ❌ paywall partout | 30 jours après expiration crédit |
| **GELÉ** | ❌ direct ; export RGPD sur demande email | ❌ direct | ❌ | jusqu'à J+365 |
| **ARCHIVÉ** | ❌ | Cold storage | ❌ | au-delà de J+365 → anonymisation J+395 |

### Schema Postgres — extensions table `users`

```sql
ALTER TABLE users ADD COLUMN account_state VARCHAR(16) DEFAULT 'active'
  CHECK (account_state IN ('active','grace','frozen','archived'));
ALTER TABLE users ADD COLUMN credit_expires_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN last_valid_otp_hash VARCHAR(128);
ALTER TABLE users ADD COLUMN last_valid_otp_expires_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN state_changed_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN first_signup_phone_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN first_signup_method VARCHAR(20);
  -- 'sms_firebase' | 'sms_at' | 'vendor' | 'diaspora_portal'

CREATE INDEX idx_users_state ON users(account_state, credit_expires_at);
```

### Cron quotidien `account_state_transitions`

```sql
-- À 00:05 locale (Cloud Scheduler)
UPDATE users SET account_state='grace', state_changed_at=NOW()
  WHERE account_state='active' AND credit_expires_at < NOW();

UPDATE users SET account_state='frozen', state_changed_at=NOW(),
                 last_valid_otp_hash=NULL
  WHERE account_state='grace' AND credit_expires_at + INTERVAL '30 days' < NOW();

UPDATE users SET account_state='archived', state_changed_at=NOW()
  WHERE account_state='frozen' AND credit_expires_at + INTERVAL '365 days' < NOW();

-- Notification J+330 (warning anonymisation)
INSERT INTO notifications (...) FROM users WHERE ...
```

### Endpoints auth

```
POST /api/v1/auth/signup/sms              # 1ère inscription : envoie SMS OTP via Firebase
POST /api/v1/auth/signup/verify           # vérifie OTP SMS + débloque 3 scans à vie

POST /api/v1/auth/login                   # phone + OTP (vendor ticket OU last_valid_otp en grace)
                                          # → renvoie état compte + accès accordé

GET  /api/v1/me/account-state             # active | grace | frozen | archived
GET  /api/v1/me/credit-status             # remaining_scans, expires_at, days_until_freeze

POST /api/v1/auth/recover                 # request export RGPD si state=frozen
                                          # → email DPO sous 30j (Art. 12)
```

### Réponse `/auth/login` selon état

```json
// État ACTIF
{ "state": "active", "token": "jwt...", "credit": { "remaining": 47, "expires_at": "..." } }

// État GRACE (J+0 à J+30)
{
  "state": "grace",
  "token": "jwt_readonly...",
  "days_remaining_grace": 12,
  "credit_expired_at": "2026-04-20T...",
  "message": "Lecture seule. Renouvelle pour reprendre les scans.",
  "paywall": true
}

// État GELÉ (J+30+)
{
  "state": "frozen",
  "error": "account_frozen",
  "message": "Ton compte est suspendu. Achète un ticket chez un vendeur pour réactiver.",
  "data_export_url": "mailto:dpo@nasoma.app?subject=Export%20donnees%20{phone}"
}
```

## Multi-tenant

Cf. §20 BP : **Tenant = pays** (KM, KE, TZ, CD).
Chaque tenant a son knowledge graph (curriculum local) et sa configuration (langue, devise, gateway MoMo).

**MVP** : un seul tenant `KM` (Comores) en base, mais le schéma porte `tenant_id` partout (anticipation Y2 sans refactor).

## Règles métier (§18 BP)

| ID | Règle | Implémentation |
|---|---|---|
| **R01** | Un scan = un événement diagnostiqué (pas de scan multiple groupé en MVP) | endpoint `POST /scans` traite 1 image |
| **R02** | Profil compétence MAJ uniquement après validation user du diagnostic | écran diagnostic avec bouton "Valider et apprendre" |
| **R03** | Concept "maîtrisé" = 3 réussites consécutives sur 3 sessions différentes (anti-luck) | service `mastery_service.py` |
| **R04** | Concept "bloqué" = 2 échecs en 7 jours | service `mastery_service.py` |
| **R05** | Rapport SMS parent envoyé uniquement plan Family, dimanche 19h heure locale | Cloud Scheduler cron `0 19 * * 0` |
| **R06** | Quota plan gratuit | **OVERRIDE : 3 scans à vie** (cf. notre échange, pas 5/jour comme BP) |
| **R07** | Quota plans payants | **OVERRIDE : selon plan (5/24h, 30/sem, 120/mois)** |
| **R08** | Crédit Mobile Money expire 90 jours après dernier achat | enforced par `expires_at` Firestore |
| **R09** | Données enfant < 13 ans = consentement parent explicite | table `consent_log` |
| **R10** | Tout contenu LLM passé par filtre modération | Vertex AI Safety + whitelist concept_code |
| **R11** | Séance validée si > 75 % d'exercices réussis | endpoint `POST /sessions/{id}/complete` |

## Critères MVP (§19 BP) — Definition of Done

- [x] Stack technique (✅ scaffolding fait)
- [ ] APK signé installable, taille < 30 MB
- [ ] Flow complet Scan → Diagnostic → Rattrapage end-to-end
- [ ] OCR fonctionnel sur 80 %+ de 200 copies test
- [ ] Knowledge Graph 500+ concepts (Maths + Français CM1-CM2)
- [ ] 100 micro-exercices validés pédagogiquement
- [ ] Authentification OTP fonctionnelle
- [ ] Paiement Hollo Money intégré
- [ ] Dashboard parent basique
- [ ] Mode offline : profil + exercices téléchargés
- [ ] Crashs < 1 % des sessions (Crashlytics)
- [ ] Scan → Diagnostic en < 8 secondes P95 sur Android entry-level

## ❌ Hors périmètre — Suivi scolaire classique (Track A)

> **Décision stratégique (2026-05-20) :** Nasoma ne fait PAS de suivi scolaire classique.
> - Pas de notes en temps réel
> - Pas de liste d'appel / pointage présence
> - Pas de bulletin numérique
> - Pas de gestion enseignant
>
> Ces modules (F25-F32 du Business Plan) sont **explicitement écartés**.
> Raison : positionnement soutien scolaire personnalisé (cf. `strategie_Nasoma.md`).

## Indicateurs CT/MT/LT — Cœur de la valeur

Nasoma délivre des **indicateurs de trajectoire d'apprentissage** sur 3 horizons :

| Horizon | Fréquence | Format | Action |
|---|---|---|---|
| **Court terme** | Quotidien | Push FCM + écran home | Exercices ciblés pour demain |
| **Moyen terme** | Hebdo + mensuel | Push FCM + écran "Rapport hebdo" in-app | Ajustement de la routine |
| **Long terme** | Trimestre + année | Push FCM + rapport agrégé in-app + examen blanc | Décision pédagogique (orientation, soutien renforcé) |

> **Décision (2026-05-20)** : aucun SMS pour rapports/notifications. Tout passe par **push FCM + écrans in-app** (gratuit). SMS uniquement pour OTP auth.

### Tables Postgres associées

```sql
-- Snapshot quotidien de maîtrise (pour calcul tendances)
mastery_snapshots (
  id UUID PK, tenant_id UUID,
  student_id UUID, concept_id UUID,
  mastery_probability FLOAT,
  snapshot_date DATE,
  PRIMARY KEY (student_id, concept_id, snapshot_date)
)

-- Indicateurs agrégés CT/MT/LT (matérialisés via cron quotidien)
student_indicators (
  id UUID PK, tenant_id UUID, student_id UUID,
  horizon VARCHAR(8),       -- 'ct' (jour) | 'mt' (semaine/mois) | 'lt' (trimestre/année)
  period_start DATE, period_end DATE,
  metrics JSONB,            -- { mastery_avg, concepts_acquired, concepts_blocked, trend_slope, ... }
  recommendations JSONB,    -- [ { action, target_concept_code, rationale }, ... ]
  computed_at TIMESTAMPTZ
)
```

## Corpus de scans archivés (Moat #1)

Chaque scan est **conservé indéfiniment** (sauf demande de suppression RGPD). C'est l'actif Moat #1.

```sql
scan_archives (
  id UUID PK, tenant_id UUID,
  student_id UUID NOT NULL,
  scan_id UUID REFERENCES scans(id),
  image_storage_key VARCHAR(256),       -- Cloud Storage path (NOT deleted at TTL)
  thumbnail_storage_key VARCHAR(256),
  ocr_text TEXT,                        -- texte extrait final
  diagnostic_summary TEXT,               -- résumé humain (1 phrase)
  exercises_detected JSONB,              -- structure complète diagnostic
  concepts_touched UUID[],
  scan_quality_score FLOAT,              -- 0-1, pour fine-tuning OCR
  subject VARCHAR(20), grade_level VARCHAR(8),
  created_at TIMESTAMPTZ,
  is_archived_consent BOOLEAN DEFAULT TRUE   -- false = parent demande suppression
)

CREATE INDEX idx_scan_archives_student_date ON scan_archives(student_id, created_at DESC);
CREATE INDEX idx_scan_archives_subject ON scan_archives(subject, grade_level);
```

**Distinction `scans` vs `scan_archives` :**
- `scans` = workflow opérationnel (TTL 30j sur l'image originale dans Storage chaud)
- `scan_archives` = actif pédagogique (image en Storage froid, conservée indéfiniment)

**Usage du corpus :**
- Affichage historique élève (consultable par le parent)
- Calcul des indicateurs CT/MT/LT (séries temporelles d'erreurs)
- Fine-tuning futur d'un OCR spécialisé écriture manuscrite enfant africain francophone
- Statistiques agrégées anonymes ("60 % des CM2 comoriens oublient la retenue")

## Spaced Repetition (Moat #6)

```sql
-- Programmation des révisions espacées par concept maîtrisé
spaced_reviews (
  id UUID PK, tenant_id UUID,
  student_id UUID, concept_id UUID,
  scheduled_for DATE NOT NULL,
  interval_days SMALLINT,    -- 1, 7, 30, 90
  status VARCHAR(16),         -- 'scheduled' | 'completed' | 'failed' | 'skipped'
  completed_at TIMESTAMPTZ,
  outcome VARCHAR(16),        -- 'retained' | 'forgotten' | 'partial'
  PRIMARY KEY (id)
)

CREATE INDEX idx_spaced_due ON spaced_reviews(scheduled_for) WHERE status = 'scheduled';
```

Cron quotidien à 6h locales : génère les sessions de révision du jour.

## Examens blancs (Moat #6)

```sql
mock_exams (
  id UUID PK, tenant_id UUID,
  student_id UUID,
  exam_type VARCHAR(20),      -- 'CEPE' | 'BEPC' | 'trimester'
  trimester SMALLINT,
  school_year VARCHAR(10),
  exercises JSONB,             -- ensemble d'exos générés
  duration_minutes INTEGER,
  started_at TIMESTAMPTZ, completed_at TIMESTAMPTZ,
  score NUMERIC(5,2),
  max_score NUMERIC(5,2) DEFAULT 20.00,
  national_avg_estimate NUMERIC(5,2),   -- "où il se situerait au CEPE"
  detailed_report JSONB
)
```

## Boucles d'engagement (Moat #1 renforcé)

```sql
-- Streak par étudiant
student_streaks (
  student_id UUID PK,
  tenant_id UUID,
  current_streak_days INTEGER DEFAULT 0,
  longest_streak_days INTEGER DEFAULT 0,
  last_activity_date DATE,
  updated_at TIMESTAMPTZ
)

-- Événements d'engagement (analytics + recommandations rétention)
engagement_events (
  id BIGSERIAL PK,
  tenant_id UUID,
  user_id UUID,                       -- parent OU étudiant
  event_type VARCHAR(40),              -- 'scan' | 'session_completed' | 'report_read'
                                       -- 'recommendation_followed' | 'share_whatsapp'
                                       -- 'referral_invited' | 'referral_redeemed'
  payload JSONB,
  created_at TIMESTAMPTZ
)
CREATE INDEX idx_engagement_user_date ON engagement_events(user_id, created_at DESC);

-- Score d'engagement consolidé (mise à jour quotidienne)
engagement_scores (
  user_id UUID PK,
  tenant_id UUID,
  score INTEGER,                       -- 0-100
  scan_frequency_score INTEGER,        -- 0-40
  session_score INTEGER,               -- 0-30
  report_read_score INTEGER,           -- 0-20
  recommendation_followed_score INTEGER, -- 0-10
  at_risk_churn BOOLEAN,
  computed_at TIMESTAMPTZ
)
```

## Programme de parrainage (Moat #7)

```sql
referral_codes (
  code VARCHAR(8) PK,                  -- 'MIMI-FAT9' (parent unique)
  tenant_id UUID,
  referrer_user_id UUID NOT NULL,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ
)

referrals (
  id UUID PK,
  tenant_id UUID,
  referral_code VARCHAR(8) REFERENCES referral_codes(code),
  referee_user_id UUID NOT NULL,        -- le filleul
  redeemed_at TIMESTAMPTZ,
  bonus_months_granted_to_referrer SMALLINT DEFAULT 1,
  bonus_months_granted_to_referee SMALLINT DEFAULT 1,
  status VARCHAR(16)                    -- 'pending' | 'confirmed' | 'cancelled'
)

CREATE INDEX idx_referrals_referrer ON referrals(referral_code);
```

Plafond : 12 mois cumulables par parrain (anti-abuse). Filleul doit avoir payé son premier ticket pour activer le bonus (anti-fraude).

### Endpoints API

```
# Indicateurs CT/MT/LT
GET  /api/v1/students/{id}/indicators?horizon=ct          # aujourd'hui
GET  /api/v1/students/{id}/indicators?horizon=mt          # semaine + mois
GET  /api/v1/students/{id}/indicators?horizon=lt          # trimestre + année
GET  /api/v1/students/{id}/trajectory                     # série temporelle BKT
GET  /api/v1/students/{id}/recommendations/daily          # actions suggérées J+1

# Corpus de scans (Moat #1)
GET  /api/v1/students/{id}/scans/history?from=&to=        # historique chronologique
GET  /api/v1/scans/{id}/archive                           # détail scan archivé (image + diagnostic)

# Spaced Repetition (Moat #6)
GET  /api/v1/students/{id}/reviews/due                    # révisions dues aujourd'hui
POST /api/v1/reviews/{id}/complete

# Examens blancs (Moat #6)
POST /api/v1/students/{id}/mock-exams                     # générer un examen blanc
GET  /api/v1/students/{id}/mock-exams/{id}/report

# Engagement (Moat #1, #7)
GET  /api/v1/me/streak
GET  /api/v1/me/engagement-score                          # admin/internal uniquement
POST /api/v1/me/share-report                              # partage WhatsApp rapport hebdo (génère image PNG)

# Parrainage (Moat #7)
GET  /api/v1/me/referral-code
POST /api/v1/auth/redeem-referral                         # à l'inscription du filleul
GET  /api/v1/me/referrals                                 # bilan parrainages
```

## Endpoints offline-first

### `GET /api/v1/kg?since={timestamp}`
Sync delta du Knowledge Graph pour cache mobile (Drift SQLite).

```json
// Response 200
{
  "since": "2026-05-19T00:00:00Z",
  "concepts_added": [...],
  "concepts_updated": [...],
  "concepts_removed": ["MATH_CM1_OBSOLETE"],
  "as_of": "2026-05-20T12:34:00Z"
}
```

### Mode offline mobile

Table Drift `local_scans_pending` :
- `id`, `file_path`, `payload_json`, `created_at`, `retries`, `last_error`
- Sync via `connectivity_plus` listener → `SyncService` dépile la queue

Cache exercices : 20 exercices "à venir" pré-fetchés selon BKT (background isolate).

## Référence rapide

| Composant | Version | Doc |
|---|---|---|
| Flutter | 3.22+ | flutter.dev |
| FastAPI | 0.115 | fastapi.tiangolo.com |
| Postgres | 16 | postgresql.org |
| Firestore | Native mode | firebase.google.com |
| Gemini | 1.5 Flash-8B, 2.0 Flash | ai.google.dev |
| Terraform | 1.9+ | hashicorp/google ~> 6.10 |
