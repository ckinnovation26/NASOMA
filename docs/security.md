# Nasoma — Sécurité & Conformité

## Cadre

- **RGPD** : applicable (utilisateurs EU possibles, équipe en France)
- **COPPA** (US Children's Online Privacy Protection Act) : applicable si extension US
- **Loi Comores** sur la protection des données personnelles : à valider avec juriste local
- **Mineurs** : règles spécifiques — consentement parental horodaté obligatoire

## Principes

1. **Privacy by design** : collecte minimale, retention minimale
2. **Zero secret in code** : tout secret dans Secret Manager
3. **Encryption everywhere** : TLS 1.3 in-flight, AES-256 at-rest
4. **Audit trail** : tout accès à des PII enfant logué
5. **Right to be forgotten** : endpoint `/me/delete` complet (GDPR Art. 17)

## Stack sécurité

| Couche | Protection |
|---|---|
| Transport | TLS 1.3 obligatoire (HSTS), reject TLS < 1.2 |
| Auth | Firebase Phone OTP + JWT RS256 |
| Tokens | Access 60min, refresh 30j, rotation |
| Données at-rest | Cloud KMS (AES-256-GCM) |
| Secrets | Cloud Secret Manager |
| PII | Chiffrement applicatif (nom, dob, numéro) |
| API | Rate limiting + CORS strict + CSRF (cookies SameSite) |
| Images | Bucket privé, signed URLs 1h max |
| LLM | Vertex AI Safety Filters BLOCK_MEDIUM_AND_ABOVE |

## Données personnelles collectées

### Élève (mineur)
- **Identifiant** : `student_id` UUID (pas de prénom requis)
- **Optionnel** : prénom, date de naissance (pour adapter exos)
- **Stocké chiffré** : oui (Cloud KMS)
- **Durée de rétention** : tant que compte famille actif + 90 jours après suppression

### Parent (majeur)
- **Numéro téléphone** : hashé SHA-256 dans la DB principale (clair uniquement dans Firebase Auth)
- **Email** (optionnel) : pour rapports hebdo
- **Consentement** : horodaté, IP enregistrée, version des CGU acceptée

### Scans
- **Image originale** : Cloud Storage 30 jours puis suppression automatique
- **Texte extrait + diagnostic** : Postgres, gardés pour BKT
- **Pas de partage** avec tiers (jamais)

## Consentement mineurs

```
Parent crée compte famille ──► accepte CGU + politique confidentialité
                            ──► coche "Je suis le parent/tuteur légal"
                            ──► saisit prénom enfant
                            ──► consent horodaté dans `consent_log`
                            ──► child profile activé
```

Table `consent_log` :
```sql
CREATE TABLE consent_log (
    id UUID PRIMARY KEY,
    parent_user_id UUID NOT NULL,
    student_id UUID NOT NULL,
    consent_type VARCHAR(50),
    consented_at TIMESTAMPTZ,
    ip_address INET,
    cgu_version VARCHAR(10),
    privacy_version VARCHAR(10)
);
```

## Modération IA

- **Génération exercices** : Vertex AI Safety BLOCK_MEDIUM_AND_ABOVE sur toutes catégories
- **Validation post-LLM** : whitelist concept_code, refus si hors curriculum
- **Pas de chat libre** avec l'enfant en V1 (chat Sprint P1, modéré strict)
- **Filtres applicatifs** :
  - Pas de noms étrangers (préférer Ali, Fatima, Said, Mariama)
  - Pas de références culturelles non-africaines
  - Pas de prix en € (utiliser KMF ou contexte abstrait)
  - Vocabulaire niveau enfant

## Right to be forgotten

Endpoint `DELETE /api/v1/me`
- Anonymise tous les `student_id` liés au compte parent
- Supprime les scans du bucket Cloud Storage
- Conserve les agrégats anonymisés (BI) sans PII
- Supprime le compte Firebase Auth après 30j de grâce
- Log de suppression conservé 1 an (preuve de conformité)

## Cycle de vie compte & rétention données (modèle "ligne téléphonique")

Cf. [`strategie_Nasoma.md`](strategie_Nasoma.md) section 3 quater.

| État | Conservation données | Accès utilisateur | Conformité RGPD |
|---|---|---|---|
| ACTIF | Tout actif (hot storage) | Complet | ✅ Art. 6 (consentement service) |
| GRACE (30j) | Tout actif | Lecture seule + export self-service | ✅ Art. 15 (accès) |
| GELÉ (J+31 à J+365) | Tout conservé (warm storage) | Pas d'accès direct ; export RGPD sur demande sous 30j (email DPO) | ✅ Art. 12 (réponse < 30j) + Art. 15 |
| ARCHIVÉ (>J+365) | Cold storage | Anonymisation par défaut à J+395 sauf opt-in | ✅ Art. 5(1)(e) data minimization |

### Engagements RGPD

- **Art. 15 (droit d'accès)** : honoré inconditionnellement. Période GRACE = self-service. Au-delà = email DPO sous 30j.
- **Art. 17 (effacement)** : honoré inconditionnellement à tout moment via `DELETE /api/v1/me` ou email DPO.
- **Art. 20 (portabilité)** : export PDF/JSON disponible en tout état (active, grace, frozen).
- **Art. 12(5)** : Nasoma se réserve le droit de refuser des demandes manifestement infondées ou excessives (anti-abus).

### CGU à publier (extrait obligatoire)

> *"Votre abonnement Nasoma fonctionne comme une ligne téléphonique prépayée. Sans crédit actif, votre compte entre en mode lecture seule pendant 30 jours, durant lesquels vous gardez l'accès à toutes vos données. Au-delà de 30 jours sans renouvellement, votre compte est suspendu. Vos données restent conservées 12 mois supplémentaires. Vous pouvez à tout moment demander l'export ou la suppression de vos données par email à dpo@nasoma.app."*

### Comptes mineurs spécifiquement

- Le parent reste **toujours** maître des données de l'enfant
- Demande d'export ou suppression du compte mineur = traitement prioritaire < 7j (vs 30j adultes)
- En cas de compte mineur GELÉ : pas d'anonymisation automatique sans tentative de contact préalable au parent par email + push
- COPPA + RGPD-K : conservation minimale par défaut

## Logs & audit

- **Tous les accès à des PII enfant** loggés dans Cloud Logging avec :
  - `correlation_id`, `actor_user_id`, `target_student_id`, `action`, `result`
- **Rétention logs** : 90 jours hot (Cloud Logging), 1 an cold (BigQuery)
- **Pas de PII dans les logs** (numéros, prénoms hashés/maskés)

## Tests de sécurité

- **Pre-commit** : detect-secrets, gitleaks
- **CI** : Snyk vulnerability scanning sur dépendances
- **Pen-test** : prévoir audit externe avant lancement public (Q3 2026)
- **Bug bounty** : à mettre en place Y2 (HackerOne ou direct contact `security@ckinnovation.fr`)

## Incident response

1. **Détection** : alerting Crashlytics / Cloud Monitoring
2. **Containment** : kill-switch + révocation tokens
3. **Eradication** : patch + déploiement urgent
4. **Notification** :
   - **Brèche PII** → CNIL France sous 72h + utilisateurs concernés
   - **Mineurs concernés** → notification parents par SMS + email
5. **Post-mortem** : sous 7 jours

## Conformité magasin Google Play

- **Family Policy** : oui (cible enfants)
- **Designed for Families** : à activer dans Play Console
- **Privacy Policy** publiée sur `nasoma.app/privacy`
- **Data Safety form** : tout déclaré dans Play Console

## Roles / Permissions

| Role | Permissions |
|---|---|
| `student` | Scans son propre profil, voit son profil compétence |
| `parent` | Manage family profiles, voit rapports, achète crédits |
| `teacher` (B2B Y2) | Voit ses classes, heatmap, pas de scans |
| `school_admin` (B2B Y2) | Manage classes, négocie quotas |
| `support` | Lecture seule, anonymisé |
| `admin` | Tout, audit log obligatoire |

## Checklist sécurité avant launch

- [ ] Pen-test externe passé
- [ ] CGU + Politique confidentialité validés juridiquement
- [ ] Consentement mineur testé end-to-end
- [ ] Right to be forgotten testé end-to-end
- [ ] Tous les secrets dans Secret Manager (zero dans le code)
- [ ] Cloud KMS configuré pour PII
- [ ] Backup Postgres testé (restore en < 1h)
- [ ] Kill-switch budget testé
- [ ] Rate limiting testé (load test)
- [ ] Crashlytics + Sentry actifs
