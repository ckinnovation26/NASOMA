# Nasoma — Modèle tarifaire & anti-abus

## Principe directeur

> **AUCUN scan gratuit illimité, jamais.**
> La gratuité = découverte uniquement. Chaque scan consomme du crédit (technique réel + valeur perçue).

## Plans

| Plan | Prix (KMF) | Prix (€) | Quota | Cible |
|---|---|---|---|---|
| **Découverte** | 0 | 0 | **3 scans / 7 jours** | Acquisition / démo écoles |
| **Ticket Journalier** | 100 | ~0,20 | 5 scans / 24h | Occasionnel |
| **Ticket 3 Jours** | **250** | **~0,50** | **15 scans / 3 jours** | **Préparation examen / week-end intensif** |
| **Hebdo** | 500 | ~1,00 | 30 scans / 7 jours | Usage régulier |
| **Mensuel (par enfant)** | **1 500/enfant** | **~3,00/enfant** | **120 scans/mois/enfant · rapports in-app illimités** | **Cœur de cible** |
| **École B2B** | 10 000–50 000 | ~20–100 | Quota par classe + dashboard | Pilote écoles privées |

### Pourquoi le Ticket 3 Jours (sweet spot tactique)

- **16,7 KMF / scan** (vs 20 KMF Journalier — meilleur rapport)
- **83 KMF / jour** (vs 100 KMF Journalier — meilleur rapport)
- **5 scans / jour** maximum effectif (idéal pour révision intensive)
- Cas d'usage type : "Examen dans 3 jours, on intensifie" → le parent achète au lieu de 3 tickets journaliers (300 KMF) = **gain 50 KMF + plus de scans**
- Économise 1 voyage chez le vendeur (achat unique vs 3 quotidiens)

### Plan Mensuel — tarification linéaire par enfant

Chaque profil enfant ajouté au compte famille est facturé séparément. Pas de forfait, pas de remise multi-enfants en MVP.

| Nombre d'enfants | Total mensuel KMF | Total ~€ | Scans/mois total |
|---|---|---|---|
| 1 enfant | 1 500 | 3 € | 120 |
| 2 enfants | 3 000 | 6 € | 240 |
| 3 enfants | **4 500** | **9 €** | 360 |
| 4 enfants (max) | 6 000 | 12 € | 480 |

**Crédits non partageables entre profils** (anti-arbitrage — un parent ne peut pas faire scanner ses 4 enfants sur un seul abonnement). Si un enfant épuise ses 120 scans, le parent doit acheter un ticket complémentaire (journalier/hebdo) pour cet enfant.

**Pas de remise multi-enfants en MVP** — à réévaluer Y2 quand la rétention M+3 sera connue.

### Détails plan Découverte

- **3 scans, point.** Pas par jour, pas par mois — à vie.
- Permet à un élève de tester sur 1-2 matières puis paywall.
- Démo en école : QR code → +1 scan crédité pour l'élève qui scanne.

### Pourquoi pas de plan annuel ?
- Pouvoir d'achat limité aux Comores → préférer micro-paiements mensuels.
- Y2 : envisager annuel avec -20 % uniquement si rétention M+3 > 60 %.

## Économie unitaire

### Coûts par scan

| Étage | Probabilité | Coût | Coût attribué |
|---|---|---|---|
| ML Kit on-device | 60 % | 0 $ | 0 $ |
| Cloud Vision | 35 % | 0,0015 $ | 0,000525 $ |
| Gemini Flash 2.0 (image) | 5 % | 0,005 $ | 0,00025 $ |
| Gemini Flash-8B (mapping + 4 exos) | 100 % | 0,0008 $ | 0,0008 $ |
| Stockage + bandwidth | 100 % | 0,00005 $ | 0,00005 $ |
| **TOTAL marginal** | | | **~0,0016 $ ≈ 1 centime KMF** |

### Marge par plan

| Plan | Revenu/scan | Coût/scan | Marge | Marge % |
|---|---|---|---|---|
| Découverte | 0 | 0,0016 $ | -0,0016 $ | -∞ (acquisition) |
| Journalier (5 scans / 100 KMF) | 0,040 $ | 0,0016 $ | 0,038 $ | **96 %** |
| **3 Jours (15 scans / 250 KMF)** | **0,033 $** | **0,0016 $** | **0,032 $** | **95 %** |
| Hebdo (30 scans / 500 KMF) | 0,033 $ | 0,0016 $ | 0,032 $ | **95 %** |
| Mensuel par enfant (120 scans / 1500 KMF) | 0,025 $ | 0,0016 $ | 0,023 $ | **93 %** |

### ARPU famille (par compte parent)

| Profil parent | Revenu mensuel KMF | Revenu ~$ |
|---|---|---|
| Famille 1 enfant | 1 500 | 3 $ |
| Famille 2 enfants | 3 000 | 6 $ |
| Famille 3 enfants (moyenne cible) | 4 500 | 9 $ |
| Famille 4 enfants | 6 000 | 12 $ |

**ARPU moyen cible** : ~3 000 KMF / compte parent / mois (hypothèse 2 enfants en moyenne).

### CAC / LTV cibles

- **CAC** (acquisition) : < 1 € via démo école + bouche-à-oreille
- **LTV cible** : > 12 € (4 mois × plan famille moyen)
- **Ratio LTV/CAC** : > 12× (très sain)
- **Payback period** : < 1 mois

### Politique "Always Give Value" — Fallback en cas d'échec OCR

> **Principe (2026-05-20) :** un parent qui paie ne doit JAMAIS sortir avec rien dans les mains, même si le scan est illisible.

#### Scénarios couverts
| Situation | Action |
|---|---|
| Scan flou / sombre / hors-cadre | OCR refusé → bascule **fallback exercises** depuis profil BKT |
| OCR OK mais pas d'exercices détectés (photo de la mauvaise page) | Même chose : fallback depuis profil |
| Devoir illisible (écriture trop déchirée) | Idem |
| Erreur réseau / Cloud Vision down | Idem |

#### Comportement fallback — flow refiné en 3 étapes (2026-05-20)

**Étape 1 — Scan #1 illisible : proposer un retry GRATUIT**
- Message : *"📷 Image difficile à lire. Veux-tu reprendre la photo ?"*
- Bouton **[Reprendre]** (gratuit dans `FALLBACK_RESCAN_GRACE_MINUTES` = 5 min)
- Bouton **[Continuer sans rescan]** → passe directement à l'étape 2
- Scan #1 reste `PROCESSING` pendant la fenêtre de retry

**Étape 2 — Retry encore illisible : modal contexte parent**
- Message : *"Ne t'inquiète pas — voici des exercices adaptés au niveau d'Ali."*
- Modal contextuel apparaît :
  ```
  📝 Aidons-nous à mieux t'aider
  Matière concernée : [Math — pré-rempli, modifiable]
  Niveau : [CM2 — pré-rempli, modifiable]
  Note récente (si tu en as une) : [_____] / 20
  Quel est le sujet du devoir ?
  ⌨️ [_______________________]  (texte libre, max 200 chars)
  [Continuer]
  ```
- Exercices générés à partir de :
  - Profil BKT existant (concept le plus faible filtré par matière)
  - Matière confirmée par le parent
  - **Indice de note** : si bas (< 10/20) → cibler les fondamentaux du grade_level
  - **Mots-clés du commentaire** extraits via Gemini Flash pour mieux cibler
  - Le grade_level (modifiable)

**Étape 3 — Récurrence (3+ scans illisibles en 7j) : assistance**
- AI affiche : *"On dirait que les photos ont du mal à être lues régulièrement. Veux-tu de l'aide ?"*
- 3 options :
  1. **"C'est mon téléphone / caméra"** → `VendorAssistanceRequest` créé
     - Le vendeur de proximité (dernier en historique de paiement) reçoit notification interne
     - Le vendeur contacte le parent (formation 1er niveau dispensée par Nasoma)
  2. **"Je ne sais pas bien prendre la photo"** → tutorial vidéo + option vendeur
  3. **"C'est vraiment le devoir qui est illisible"** → continuer fallback sans re-proposer assistance avant 7j

#### Formation vendeur 1er niveau (opérationnel)
- Pack de formation distribué aux vendeurs partenaires (PDF + vidéo 10 min)
- Contenu :
  - Comment vérifier la propreté de l'objectif caméra
  - Comment positionner la copie (éclairage, à plat, distance)
  - Comment activer la fonction "ajuster les bords" du téléphone
  - Quand orienter vers un changement de téléphone (cas extrême)
- Le vendeur reçoit une **commission complémentaire** (~50 KMF / cas résolu)
- Motivation à aider sans pousser à des achats inutiles

#### Quota & courtoisie
- Scan #1 illisible : non décrémenté si retry dans 5 min
- Retry illisible → décrément quota normal (coût consommé)
- Exercices fallback générés en pleine valeur (3-4 exos)
- **Re-scan gratuit "courtoisie"** offert 1× par jour pendant assistance vendeur ouverte

#### Tracking BI (métriques anti-frustration)
- `% scans → fallback` cible < 15 % (sinon problème UX caméra)
- `Net Promoter Score post-fallback` cible > 30
- `Taux de re-scan post-fallback` cible < 20 % (parent satisfait du fallback)

#### Anti-abus
- Max **1 fallback toutes les 24h** par compte (anti-spam d'images aléatoires)
- Fallback exercises tracking séparé du quota normal pour BI
- Si > 50 % des scans d'un compte sont fallback → flag suspect (review humain)

### Politique notifications (2026-05-20)

> **Aucun SMS rapport, aucun SMS notification.**
> Tout est in-app + push FCM (gratuit).
> SMS utilisé **uniquement pour la PREMIÈRE authentification** (one-shot ~0,02 $/inscription, amorti sur LTV).
> Tous les renouvellements suivants = ticket vendeur (zéro SMS, zéro opérateur).

**Économie estimée Y2 à 50 000 users** : ~4 000 $/mois (200k SMS rapports évités × 0,02 $).

### Cycle de vie compte ("modèle ligne téléphonique")

> Décision 2026-05-20 : Nasoma fonctionne comme une ligne téléphonique prépayée.
> Sans crédit actif, le compte se dégrade par paliers (30j lecture seule, puis gelé).

| Phase | Durée | Accès utilisateur | Coût infra Nasoma |
|---|---|---|---|
| **ACTIF** | tant que crédit > 0 ou jours_restants > 0 | 100 % features | Plein |
| **GRACE (lecture seule)** | 30 jours après expiration | Voir historique, profil, rapports passés. Pas de nouvelle action. | Minimal (read-only) |
| **GELÉ** | de J+31 à J+365 | Accès direct impossible. Export RGPD sur demande email. | Quasi-nul (stockage warm) |
| **ARCHIVÉ** | > J+365 | Cold storage + anonymisation par défaut à J+395 (opt-in pour garder) | ~0 |

**Pourquoi 30 jours de grace** : modèle Comores Telecom / Telma — analogie immédiate pour la clientèle. Permet aussi à un parent absent (voyage, hospitalisation) de retrouver son compte intact au retour.

**Impact sur LTV** : la grâce permet le "win-back" — 25-40 % des comptes en GRACE renouvellent avant le gel.

## Mécanismes anti-abus

### 1. Compteur Firestore signé serveur
```python
# Décrément atomique via transaction
@firestore.transactional
async def consume_scan(transaction, user_id):
    quota_ref = db.collection("user_quotas").document(user_id)
    quota = (await transaction.get(quota_ref)).to_dict()
    if quota["remaining"] <= 0:
        raise QuotaExhausted()
    transaction.update(quota_ref, {"remaining": quota["remaining"] - 1})
```

### 2. pHash anti-rescan (cache 24h)
```python
phash = imagehash.phash(image)
cached = await firestore.get(f"scan_cache/{user_id}/{phash}")
if cached and (now - cached.created_at) < timedelta(hours=24):
    return cached.diagnostic   # PAS de décrément
```

### 3. Throttle device fingerprint
```python
# Token bucket par device : 20 scans/heure
if device_scans_this_hour(device_id) >= 20:
    raise RateLimited(retry_after=3600)
```

### 4. Pre-flight quota check côté mobile
```dart
// AVANT d'ouvrir la caméra
final quota = await api.checkQuota();
if (!quota.allowed) {
  context.go('/paywall');
  return;
}
// open camera...
```

### 5. Compression obligatoire côté serveur
```python
if len(image_bytes) > 200_000:
    raise HTTPException(413, "image_too_large")
```

### 6. Budget hard-cap par tenant
```python
# Cloud Function `daily-budget-check`
if tenant_spend_today > tenant_daily_budget:
    disable_apis_for_tenant(tenant_id)
    notify_admin(tenant_id)
```

### 7. Tickets physiques HMAC
```
Code: NSMA-A3F2-9B1C-7D4E
HMAC: sha256(code | plan | batch_id | SECRET)
```
- Génération en lots de 1000 codes par batch
- Vendus en kiosque (papier scratch)
- Activation unique (collection `redeemed_tickets` Firestore)

### 8. Pas de transfert entre comptes
```python
# Aucun endpoint /family/transfer-credits
# Les crédits sont liés au family_id, partagés entre 4 profils max
```

### 9. Expiration stricte
- Journalier : 24h
- Hebdo : 7 jours
- Mensuel : 30 jours
- **Pas de carry-over** des crédits non utilisés.

### 10. Quota Cloud Vision + Gemini par tenant
- Quota par défaut : 100 requêtes Vision/jour/tenant
- Au-delà : 503 + alerte admin
- Augmentation manuelle uniquement

## Génération des tickets physiques

```bash
cd backend
python -m scripts.generate_recharge_codes \
  --plan monthly_family \
  --count 1000 \
  --batch-id BATCH-2026-05 \
  --output tickets_batch_2026_05.csv
```

CSV format :
```csv
code,hmac,plan,batch_id,created_at
NSMA-A3F2-9B1C-7D4E,abc123...,monthly_family,BATCH-2026-05,2026-05-19T10:00:00Z
```

→ Imprimer sur cartes papier scratch avec QR code (l'élève peut scanner au lieu de taper).

## Conformité paiement

### Hollo Money (Comores — priorité MVP)
- API REST + webhook HMAC
- Frais : 1,5 % par transaction
- KYC : géré côté Hollo

### Mvola, M-Pesa, Orange Money, Airtel Money (post-MVP)
- Abstraction provider commune : `app/services/payment/providers/`
- Tous les webhooks normalisés sur le même schéma interne

### Stripe (Y2 — paiements internationaux)
- Activation après validation produit-marché en Comores
- Stripe Tax pour TVA OSS si extension Europe
