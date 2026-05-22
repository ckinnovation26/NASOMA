# Nasoma — Référence API REST

> Base URL :
> - Dev : `http://localhost:8000`
> - Prod : `https://api.nasoma.app`
>
> Toutes les routes sont préfixées par `/api/v1`.
> Docs OpenAPI auto-générées : `/docs` (dev uniquement).

## Authentification

Toutes les routes (sauf `/auth/*` et `/health`) exigent un header `Authorization: Bearer <JWT>`.

### `POST /api/v1/auth/exchange`
Échange un Firebase ID Token contre un JWT applicatif avec custom claims.

```json
// Request
{ "firebase_id_token": "eyJhbGc..." }

// Response 200
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "usr_abc123",
    "phone": "+269XXXXXXXX",
    "role": "student",
    "plan": "discovery"
  }
}
```

## Quotas — `/api/v1/quota`

### `GET /quota`
Solde de scans restant + plan actif.

```json
// Response 200
{
  "remaining_scans": 2,
  "plan": "discovery",
  "lifetime_remaining": 2,
  "expires_at": null
}
```

### `POST /quota/check`
Pre-flight check côté mobile — appelé AVANT d'ouvrir la caméra.

```json
// Response 200
{ "allowed": true, "remaining": 2 }

// Response 402 Payment Required
{
  "allowed": false,
  "remaining": 0,
  "reason": "quota_exhausted",
  "paywall": { "plans": ["daily", "weekly", "monthly_family"] }
}
```

### `POST /quota/recharge`
Active un code de recharge (ticket physique).

```json
// Request
{ "code": "NSMA-A3F2-9B1C-7D4E" }

// Response 200
{
  "plan": "monthly_family",
  "scans_added": 120,
  "expires_at": "2026-06-19T12:00:00Z"
}
```

## Scans — `/api/v1/scans`

### `POST /scans`
Lance un scan. **Décrémente** atomiquement le quota.

```json
// Request (multipart/form-data)
// - image: JPEG ≤ 200 KB
// - phash: string (hash perceptuel calculé côté mobile)
// - subject: "math" | "francais" | "arabe" | "sciences"
// - grade: "CM1" | "CM2" | "6E"
// - mlkit_result: { "text": "...", "confidence": 0.87 }  // optionnel

// Response 202 Accepted
{
  "scan_id": "scn_abc123",
  "status": "processing",
  "eta_seconds": 8,
  "cached": false
}

// Response 200 si pHash match (cache hit, quota PAS décrémenté)
{
  "scan_id": "scn_abc123",
  "status": "done",
  "cached": true,
  "diagnostic_id": "diag_xyz789"
}
```

### `GET /scans/{scan_id}`
Statut + diagnostic.

```json
// Response 200
{
  "scan_id": "scn_abc123",
  "status": "done",
  "diagnostic": {
    "exercises": [
      {
        "index": 1,
        "statement": "356 + 478",
        "student_answer": "724",
        "is_correct": false,
        "error_description": "Oubli de la retenue",
        "concept_code": "MATH_CM2_NUM_ADD_RETENUE",
        "confidence": 0.92
      }
    ],
    "session_id": "ses_def456"
  }
}
```

## Sessions — `/api/v1/sessions`

### `GET /sessions/{session_id}`
Récupère le pack d'exercices générés.

```json
{
  "session_id": "ses_def456",
  "concept_code": "MATH_CM2_NUM_ADD_RETENUE",
  "exercises": [
    {
      "id": "ex_001",
      "type": "mcq",
      "prompt": "Combien font 234 + 187 ?",
      "options": ["411", "421", "521", "311"],
      "tts_text": "Combien font deux-cent-trente-quatre plus cent-quatre-vingt-sept ?"
    }
  ]
}
```

### `POST /sessions/{session_id}/answers`
Soumet une réponse — déclenche update BKT.

```json
// Request
{
  "exercise_id": "ex_001",
  "answer": "421",
  "time_spent_seconds": 45
}

// Response 200
{
  "correct": true,
  "explanation": "Bravo ! Tu as bien retenu la retenue.",
  "new_mastery": 0.67
}
```

### `POST /sessions/{session_id}/complete`
Termine la session, retourne le bilan.

```json
{
  "completed": true,
  "concept_mastery_before": 0.42,
  "concept_mastery_after": 0.67,
  "next_concept_suggested": "MATH_CM2_NUM_SUB_RETENUE"
}
```

## Profil — `/api/v1/profile`

### `GET /profile`
Vue arborescente knowledge graph du profil actif.

```json
{
  "student_id": "stu_abc",
  "name": "Ali",
  "grade": "CM2",
  "concepts": [
    {
      "concept_code": "MATH_CM2_NUM_ADD_RETENUE",
      "mastery": 0.67,
      "status": "in_progress",
      "last_practiced": "2026-05-19T10:30:00Z"
    }
  ]
}
```

## Famille — `/api/v1/family`

### `GET /family/profiles`
Liste les profils enfants (max 4).

### `POST /family/profiles`
Crée un profil enfant.

```json
// Request
{ "name": "Fatima", "grade": "CM1", "date_of_birth": "2016-03-15" }

// Response 201
{ "student_id": "stu_xyz", "name": "Fatima", "grade": "CM1" }
```

### `POST /family/profiles/{student_id}/switch`
Active ce profil pour l'utilisateur parent (les prochains scans seront attribués à cet enfant).

## Paiement — `/api/v1/payments`

### `POST /payments/initiate`
Démarre une transaction Hollo Money / Mvola / etc.

```json
// Request
{
  "plan": "monthly_family",
  "provider": "hollo",
  "phone": "+269XXXXXXXX"
}

// Response 200
{
  "transaction_id": "txn_abc",
  "ussd_code": "*123*456#",
  "expires_at": "2026-05-19T10:35:00Z"
}
```

### `POST /payments/webhook/hollo`
Webhook reçu de Hollo (signature HMAC vérifiée).

## Erreurs

| Code | Signification |
|---|---|
| 400 | Requête malformée (validation Pydantic) |
| 401 | JWT manquant/invalide |
| 402 | Quota épuisé — payer pour continuer |
| 403 | Permission refusée (mineur sans consentement parent) |
| 404 | Ressource introuvable |
| 422 | Validation métier (ex: concept_code inconnu) |
| 429 | Rate limit (max 20 scans/h par device) |
| 503 | Budget kill-switch activé — service temporairement indisponible |

Format d'erreur :

```json
{
  "error": {
    "code": "quota_exhausted",
    "message": "Vous avez utilisé vos 3 scans découverte.",
    "details": { "plan": "discovery", "remaining": 0 }
  },
  "correlation_id": "req_abc123"
}
```

## Headers obligatoires

- `Authorization: Bearer <jwt>` — sauf `/auth/*` et `/health`
- `X-Device-Id: <android_id>` — anti-abus throttle device
- `X-App-Version: 0.1.0` — pour migrations forcées
- `Accept-Language: fr | en | sw` — sélection i18n

## Knowledge Graph sync (offline-first)

### `GET /api/v1/kg?since={iso8601}`
Récupère un delta du knowledge graph pour mise à jour du cache mobile.

```json
// Response 200
{
  "since": "2026-05-19T00:00:00Z",
  "as_of": "2026-05-20T12:34:00Z",
  "tenant": "KM",
  "concepts_added": [
    {
      "code": "MATH_CM2_ADD_RETENUE",
      "name": "Addition avec retenue",
      "difficulty": 1,
      "prerequisites": ["MATH_CM1_ADD_SIMPLE"],
      "curriculum_refs": {"APC_KM": "M.5.1.2"}
    }
  ],
  "concepts_updated": [],
  "concepts_removed": []
}
```

## Indicateurs CT/MT/LT — Trajectoire d'apprentissage

Cœur de la valeur Nasoma — cf. [`strategie_Nasoma.md`](strategie_Nasoma.md).

### `GET /api/v1/students/{id}/indicators?horizon=ct|mt|lt`

```json
// horizon=ct (court terme — aujourd'hui)
{
  "horizon": "ct",
  "as_of": "2026-05-20T18:00:00Z",
  "metrics": {
    "concepts_practiced_today": 4,
    "mastery_avg_today": 0.62,
    "delta_vs_yesterday": 0.03,
    "blocked_concept": "MATH_CM2_ADD_RETENUE"
  },
  "recommendations": [
    {
      "action": "exercise_session",
      "target_concept_code": "MATH_CM2_ADD_RETENUE",
      "rationale": "Bloqué depuis 3 jours, 2 échecs consécutifs",
      "duration_minutes": 10
    }
  ]
}

// horizon=mt (moyen terme — semaine + mois)
{
  "horizon": "mt",
  "period_start": "2026-04-20",
  "period_end": "2026-05-20",
  "metrics": {
    "concepts_acquired": 7,
    "concepts_blocked": 2,
    "mastery_trend_slope": 0.08,
    "scan_frequency_per_week": 3.2
  },
  "recommendations": [
    {
      "action": "focus_subject",
      "target_subject": "francais",
      "rationale": "Stagnation en français depuis 2 semaines",
      "minutes_per_day": 15
    }
  ]
}

// horizon=lt (long terme — trimestre + année)
{
  "horizon": "lt",
  "period_start": "2026-01-01",
  "period_end": "2026-05-20",
  "metrics": {
    "concepts_acquired_total": 28,
    "concepts_remaining_curriculum": 72,
    "projected_completion_date": "2027-03-15",
    "risk_flags": ["lecture_enonce_persistant"]
  },
  "recommendations": [
    {
      "action": "pedagogical_decision",
      "target": "lecture_enonce",
      "rationale": "Blocage récurrent depuis CM1. Risque de redoublement si non traité avant le 3ᵉ trimestre.",
      "priority": "high"
    }
  ]
}
```

### `GET /api/v1/students/{id}/trajectory`
Série temporelle BKT pour graphique d'évolution.

```json
{
  "student_id": "stu_abc",
  "subject_filter": "math",
  "points": [
    { "date": "2026-04-01", "mastery_avg": 0.42 },
    { "date": "2026-04-08", "mastery_avg": 0.48 },
    { "date": "2026-04-22", "mastery_avg": 0.57 },
    { "date": "2026-05-20", "mastery_avg": 0.62 }
  ]
}
```

### `GET /api/v1/students/{id}/recommendations/daily`
Actions suggérées pour demain (J+1).

```json
{
  "for_date": "2026-05-21",
  "actions": [
    {
      "type": "exercise",
      "target_concept_code": "MATH_CM2_ADD_RETENUE",
      "duration_minutes": 10,
      "best_time_hint": "soir avant les devoirs"
    }
  ],
  "parent_sms_summary": "Demain, faites faire à Ali 3 exos sur les retenues. C'est ce qui le bloque en ce moment."
}
```

## Notifications

```
GET    /api/v1/notifications                   # historique user
PATCH  /api/v1/notifications/{id}/read         # marquer lu
POST   /api/v1/notifications/preferences       # config canaux (push/SMS/email)
```

## ❌ Hors périmètre (Track A explicitement écarté)

Les modules **Présence**, **Notes en temps réel**, **Bulletin numérique** (F25-F32 du BP) **ne sont PAS implémentés** dans Nasoma. Cf. `strategie_Nasoma.md` pour le rationale.

## Rate limiting

| Endpoint | Limite |
|---|---|
| `POST /scans` | 20/heure/device |
| `POST /auth/*` | 5/minute/IP |
| `GET /students/{id}/indicators` | 60/minute/user |
| Autres | 100/minute/user |
