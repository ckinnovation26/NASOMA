# Nasoma — Stratégie & Moats défensifs

> Document stratégique, validé le 2026-05-20.
> À relire à chaque revue trimestrielle.

---

## 1. Repositionnement produit (critique)

### Ce que Nasoma N'EST PAS

- ❌ **Pas un correcteur de copies par IA**. Gemini, ChatGPT, Google Lens font déjà ça gratuitement. Se positionner ainsi = mort en 12 mois.
- ❌ **Pas un outil de suivi scolaire classique**. Pas de notes en temps réel, pas de liste d'appel, pas de bulletin numérique, pas de gestion de présence. Ce périmètre LISEC 2018 est **explicitement écarté**.
- ❌ **Pas un outil pour les enseignants ou les écoles**. Ce sont des canaux de distribution, pas des utilisateurs primaires.

### Ce que Nasoma EST

> **Nasoma est le coach pédagogique personnel de chaque élève africain, avec des indicateurs court / moyen / long terme et des suggestions d'actions quotidiennes pour le parent et l'enfant.**

**Le produit cœur** = soutien scolaire régulier piloté par la donnée :

| Horizon | Que produit Nasoma | Action attendue |
|---|---|---|
| **Court terme (jour J+1)** | "Aujourd'hui, Ali a buté sur les retenues — 3 micro-exercices ciblés pour demain matin" | Faire les 3 exos avant l'école |
| **Moyen terme (semaine / mois)** | "Cette semaine : +12 % de maîtrise en numération, stagnation en problèmes. Conseil : 15 min/jour sur les problèmes." | Ajuster la routine quotidienne |
| **Long terme (trimestre / année)** | "Depuis CM1, progression régulière en calcul mais blocage récurrent sur la lecture d'énoncé. Risque de redoublement si non traité avant le 3ᵉ trimestre." | Décision pédagogique (cours particulier, accompagnement renforcé, choix d'établissement) |

L'IA n'est qu'un **moyen** — la **valeur perçue** est la trajectoire d'apprentissage longitudinale et les recommandations d'action.

---

## 2. Le risque Google (constat franc)

Gemini, Google Lens, ChatGPT Vision corrigent une copie en quelques secondes, **gratuitement**, sur un téléphone bas de gamme avec une connexion 3G.

> **Conclusion :** la fonction "scan → correction" n'est PAS un moat. Elle deviendra une commodité d'ici 18-24 mois.

**Ce que Google NE FAIT PAS** (et ne fera probablement pas pour les Comores) :

1. Mémoriser l'état de maîtrise d'un élève sur 7 ans (CM1 → 3ᵉ)
2. Suggérer une action quotidienne ciblée à un parent peu scolarisé
3. Aligner les exercices sur le curriculum APC comorien (650 concepts, codes officiels)
4. Vendre des tickets de recharge papier dans un kiosque de Mutsamudu
5. Envoyer un SMS rapport dimanche soir au parent en français simple
6. Travailler hors-ligne en 2G/3G
7. Comprendre le shikomori
8. Encaisser via Hollo Money sans carte bancaire
9. Construire une relation de confiance avec des familles via la diaspora

**C'est sur ces 9 points que se construit le moat.**

---

## 3. Les 5 moats (4 actuels + 1 à construire)

### Moat #1 — Profil BKT longitudinal & corpus de devoirs scannés
**Statut : ✅ Cœur produit, à coder dès Sprint 1**

Gemini est **stateless** : il oublie tout après chaque conversation. Nasoma sait que **Ali oublie systématiquement la retenue depuis 3 semaines**, propose des exos adaptés, et trace la progression sur 7 ans.

#### Le corpus de devoirs scannés = actif unique

Chaque scan envoyé est **conservé** (image compressée + OCR + diagnostic) et devient un point de donnée dans la trajectoire d'apprentissage. Au bout de 6 mois d'usage régulier (2-3 scans/semaine), un élève accumule **~60-80 scans archivés** :

- Réutilisés comme **indicateurs CT/MT/LT** (tendances d'erreurs, évolution de l'écriture, progrès matière par matière)
- Disponibles en **historique consultable** par le parent (vue chronologique des devoirs)
- Servent à entraîner un OCR **fine-tuné spécifiquement** sur l'écriture manuscrite des enfants africains francophones (corpus propriétaire qui s'enrichit chaque mois)
- Permettent de **détecter des patterns** : "60 % des élèves CM2 comoriens oublient la retenue en colonne dizaines" → données pour adapter les exercices

> **Insight clé** : Le corpus de scans est un **actif qui prend de la valeur avec le temps**, contrairement à un correcteur ponctuel Gemini où la donnée est jetée après chaque session.

**Cost of switching** : un élève qui quitte Nasoma après 6 mois perd :
- 6 mois de profil BKT (état de maîtrise sur 100+ concepts)
- L'historique chronologique de tous ses devoirs scannés
- Les indicateurs de tendance CT/MT/LT
- Le journal des actions recommandées et leur impact

**Différenciateur** : c'est le **seul moat qui ne dépend pas d'un partenaire externe**. Il se construit purement par usage. **Plus l'élève utilise, plus le moat se renforce.**

### Moat #2 — Knowledge Graph APC_KM validé
**Statut : ⚠️ Existant en draft, validation pédagogique à OBTENIR**

650 concepts du curriculum APC comorien, avec leur DAG de prérequis, leurs erreurs types, leur difficulté. Ce graphe doit être **validé par des inspecteurs CIPR Ngazidja** (3 inspecteurs × 300-500 € forfait = ~1 500 €).

- **Sans validation institutionnelle** : c'est un graphe IA-généré sans crédibilité = pas un moat.
- **Avec validation CIPR + tampon officiel** : c'est une barrière à l'entrée de 6-12 mois pour un concurrent.

**Action prioritaire Sprint 2** : approcher 3 inspecteurs CIPR et obtenir validation écrite.

### Moat #3 — Distribution physique + paiement local
**Statut : ✅ Architecture prête, exécution à lancer en parallèle du MVP**

- **Tickets de recharge papier** (16 chars HMAC) vendus en kiosque + écoles, modèle SENELEC/Orange. Google ne distribuera jamais de tickets papier à Mutsamudu.
- **Hollo Money + Mvola** intégrés natifs. Google Pay / Stripe ne marchent pas (ou mal) aux Comores.
- **Canal diaspora** : virement France/EAU/Mayotte → Comores pour payer l'abonnement enfant. **Potentiel 50 % des paiements Y1**, totalement défendable.

**Pourquoi c'est défendable** : Google n'a pas d'incentive à monter une logistique de tickets papier pour 800 000 habitants. Le ROI est trop faible pour eux.

### Moat #4 — Canal in-app + push (habitude sticky, zéro coût récurrent)
**Statut : ✅ À coder Sprint 2**

> **Décision (2026-05-20) : aucun SMS rapport. Tout dans l'app + push FCM (gratuit).**
> SMS uniquement pour OTP à l'authentification (must-have technique).
> Économie estimée : ~4 000 $/mois en Y2 à 50 000 users (200k SMS × 0,02 $).

#### Écran "Rapport hebdo" in-app (dimanche)
Push FCM dimanche 19h heure locale : *"Le rapport d'Ali est prêt — 4 séances cette semaine."*
→ Parent ouvre l'app → écran dédié "Rapport hebdomadaire" :
- Top 3 progrès
- Top 3 lacunes en cours
- 1 action recommandée pour la semaine
- Comparaison anonyme avec la classe ("Ali est dans le top 30 % en numération")
- Bouton "Partager dans le groupe WhatsApp" (génère PNG anonymisée — cf. Moat #7)

#### Notifications push intelligentes (in-app feed + push FCM)
- **Quotidien (option Mensuel)** : "Demain, faites faire à Ali 3 exos sur les retenues."
- **Trimestriel long terme** : "Attention : la moyenne d'Ali en français a baissé de 8 points ce trimestre."
- **Tout est archivé dans l'écran "Notifications"** de l'app (consultable plus tard si push raté)

#### Pourquoi c'est sticky
- **Habitude rituelle dominicale** : le parent ouvre l'app chaque dimanche pour lire le rapport
- **Zéro coût récurrent** : FCM = gratuit, l'app étant installée
- **Push offline-safe** : la notification arrive même si l'app est fermée (Android)
- **Historique consultable** : si le parent rate la notif, le rapport reste dans l'app

#### Limite et mitigation
- **Risque** : si le parent désinstalle l'app, on perd le canal (un SMS aurait survécu)
- **Mitigation** : la valeur perçue (rapport hebdo + indicateurs CT/MT/LT + corpus scans) rend la désinstallation coûteuse. Le streak + l'engagement loop entretiennent l'usage actif.
- **Fallback** : si pas d'ouverture en 30 jours, **1 email parent** (gratuit) avec lien profond vers l'app — pas de SMS.

### Moat #5 — Partenariats institutionnels & écoles
**Statut : ❌ INEXISTANT — moat futur à construire**

> **À noter sans ambiguïté : aucun partenariat institutionnel n'est actuellement signé.**
>
> Les NDAs LISEC 2018 (Commissariat à l'Éducation de Ngazidja) sont un historique CK Innovation, mais **ne constituent pas un partenariat opérationnel pour Nasoma en mai 2026**.

**Plan de construction du moat #5 (Sprint 3 → Y2)** :

| Échéance | Cible | Livrable |
|---|---|---|
| Juin 2026 | Re-contacter Commissariat Education Ngazidja | Réunion de présentation Nasoma |
| Juillet 2026 | 3 écoles privées Moroni / Mutsamudu | LOI (Letter of Intent) pilote 200-500 élèves |
| Août 2026 | Inspecteurs CIPR | Convention validation pédagogique KG (Moat #2) |
| Décembre 2026 | Ministère Éducation Nationale Comores | Reconnaissance officielle (logo, communication) |
| Mars 2027 | UNICEF / AFD / coopération France | Co-financement déploiement public |

**Ce moat sera le plus puissant à long terme mais ne sera pas activable avant Q1 2027.** En attendant, la défense repose sur les 4 autres.

### Moat #6 — Méthode pédagogique propriétaire (Spaced Repetition + Examens blancs)
**Statut : ✅ À coder Sprint 2 (différenciateur fort vs Google)**

#### Spaced Repetition (révision espacée)
Un concept marqué "maîtrisé" (`p_known ≥ 0.85`) **n'est pas oublié par Nasoma**. Il est **re-testé automatiquement** à :
- **J+1** : vérification immédiate
- **J+7** : ancrage court terme
- **J+30** : consolidation moyen terme
- **J+90** : maîtrise long terme

Si l'élève échoue à un de ces tests, le concept retombe en "en cours" et un mini-rattrapage est programmé. **Google ne fait pas ça.** Sans Nasoma, l'élève "maîtrise" un concept en cours puis l'oublie en 3 mois — c'est pourquoi tant d'élèves "savaient" en CM1 et "ne savent plus" en CM2.

#### Examens blancs trimestriels (gratuits, inclus dans le plan Mensuel)
3 fois par an, Nasoma génère **un examen blanc complet** au format des examens nationaux comoriens (CEPE pour la fin de cycle primaire, BEPC pour 3ᵉ), aligné sur ce que l'élève a réellement étudié.

- L'enfant le passe en condition réelle (60-90 min, chronométré, pas d'aide)
- Résultat = note + analyse détaillée par compétence
- Rapport long terme au parent : "Ali serait au-dessus / au-dessous de la moyenne nationale CEPE s'il passait l'examen aujourd'hui"

> **Effet psychologique** : Le parent voit un **score officiel-like 3 fois par an**, ce qui ancre l'usage régulier de l'app pendant tout le trimestre.

#### Pourquoi c'est un moat
- **Demande un knowledge graph mature et validé** (Moat #2) pour générer un examen blanc crédible
- **Demande l'historique BKT** (Moat #1) pour adapter aux concepts effectivement étudiés
- **Spaced Repetition** demande l'infrastructure de notifications + tracking persistant
- Google ne s'investira jamais dans la pédagogie comorienne spécifique

### Moat #7 — Réseau social parents & diaspora
**Statut : ⚠️ À coder Sprint 3 (acquisition virale + sticky)**

#### Partage hebdomadaire dans groupes WhatsApp de classe
L'écran "Rapport hebdo" in-app est **partageable en 1 tap** dans le groupe WhatsApp de la classe d'Ali, sous forme d'**image PNG anonymisée** (sans le score absolu, juste "Ali a progressé de +12 % cette semaine").

Effet :
- Les autres parents voient → s'inscrivent → bouche-à-oreille intégré
- Pas d'invitation forcée — c'est le parent qui choisit de partager (et il le fera, par fierté)

#### Code de parrainage (referral)
Code unique par parent : `MIMI-FAT9` (4 chars).
- Filleul s'inscrit avec ce code → **1 mois Mensuel gratuit pour le filleul ET le parrain**
- Plafond : 12 mois cumulables par parrain (= 1 an gratuit max)
- Coût marginal pour Nasoma : ~0,001 $ × 120 × 12 = 1,44 $ par parrainage (négligeable)

#### Canal diaspora structuré
- Parent en France/EAU/Mayotte peut **abonner les enfants de sa famille restés au pays** depuis l'app (paiement Stripe ou virement)
- **Acte d'amour rationalisé** : la diaspora envoie souvent de l'argent au pays sans visibilité sur l'usage ; Nasoma fournit un **rapport mensuel précis** de ce que l'argent a financé (l'éducation des neveux/nièces)
- Potentiel cible : **50 % des paiements Y1** viennent de la diaspora

#### Pourquoi c'est un moat
- **Effet de réseau** : valeur de Nasoma augmente avec le nombre de parents dans le groupe WhatsApp d'une classe
- **Acquisition à coût quasi-nul** via les partages organiques
- **Bouche-à-oreille validé culturellement** : les Comores fonctionnent traditionnellement sur le réseau familial étendu et la diaspora

---

## 3 bis. Boucles d'engagement (Engagement Loops)

> **Insight critique :** plus le parent utilise l'app régulièrement, plus les indicateurs CT/MT/LT sont précis, plus les recommandations sont efficaces. **L'usage régulier est lui-même un moat.**

### Pourquoi inciter à l'usage régulier
- **2-3 scans/semaine** = données suffisantes pour des indicateurs CT pertinents
- **1-2 scans/jour** = profil BKT précis, recommandations chirurgicales
- Sans usage régulier → indicateurs creux → app peu utile → churn

### Mécaniques d'engagement (à coder Sprint 2-3)

#### 1. Streak parent-enfant partagé 🔥
Compteur de jours consécutifs avec au moins 1 scan OU 1 séance. Affiché en home dashboard.
- **3 jours** : "3🔥 Beau travail !"
- **7 jours** : "Une semaine complète ! Badge déverrouillé."
- **30 jours** : "Champion du mois — Ali est dans les 10 % les plus assidus de sa classe."

⚠️ **Sans gamification toxique** : pas de loot box, pas de classement public élèves, pas de monnaie virtuelle. Juste reconnaissance simple (R-éthique enfants).

#### 2. Notifications quotidiennes intelligentes
- **Heure optimale** : analyser quand le parent ouvre l'app et envoyer le SMS/push à ce moment précis
- **Message contextualisé** :
  - Lundi 18h : "Bon début de semaine — Ali a fait 3 exos. Demande-lui de scanner ses devoirs ce soir."
  - Vendredi 16h : "Le weekend approche — bon moment pour 15 min de révision sur les fractions."
- **Anti-spam** : max 1 SMS/jour, 3 push/jour

#### 3. Cascade de rappels (re-engagement — push uniquement, zéro coût)
| Jours sans scan | Action |
|---|---|
| 2 jours | Push doux : "Ali, viens scanner ta dernière dictée !" |
| 4 jours | Push parent : "Ça fait 4 jours sans scan. Ali décroche-t-il ?" |
| 7 jours | Push parent : "Reprends Nasoma ce weekend — Ali a fait des progrès, ne les perds pas." |
| 14 jours | Push parent + offre in-app : "1 ticket journalier offert pour relancer ! Code COMEBACK déjà dans l'app." |
| 30 jours | Email parent (fallback gratuit) : "Ton abonnement est en pause — voici ce que Ali a accompli en {N} mois." |

#### 4. Mini-rituel hebdomadaire (Dimanche)
- **Dimanche matin 9h** : push enfant "Prépare ton scan de la semaine !"
- **Dimanche soir 19h** : push parent "Rapport d'Ali prêt — top 3 progrès, 1 lacune, 1 action." → ouvre écran "Rapport hebdo" in-app

#### 5. Examens blancs (cf. Moat #6) — Engagement long terme
3 fois par an = 3 moments forts d'engagement intense.

#### 6. Mode "Devoir surveillé" (gratuit)
Si l'enfant a un examen demain, mode spécial 30 min de révision ciblée sur les concepts à risque selon BKT — **active automatiquement quand le parent ajoute "Examen demain"** dans l'app.

### Indicateur santé d'engagement
Un score d'engagement par compte parent (0-100) calculé sur :
- Fréquence de scan (poids 40 %)
- Sessions complétées (poids 30 %)
- Lecture rapport hebdo (poids 20 %)
- Réponse à recommandations (poids 10 %)

Affiché côté équipe Nasoma uniquement (pour identifier les comptes à risque churn et déclencher actions de rétention).

---

## 3 quater. Modèle d'authentification & cycle de vie du compte

> **Décision (2026-05-20) : indépendance totale des opérateurs téléphoniques.**

### Le modèle OTP "3-en-1"

Chaque OTP émis par Nasoma a **trois fonctions simultanées** :

| Fonction | Rôle |
|---|---|
| 🔑 Mot de passe | Authentification (combiné au numéro de téléphone qui est l'identifiant) |
| 💰 Preuve de paiement | Atteste qu'un montant a été payé pour un service précis |
| ⏳ Token de session | Définit la durée pendant laquelle le compte est "actif" (24h / 7j / 30j) |

**Conséquence** : pas d'écran "login" séparé d'un écran "recharge". **C'est le même geste.**

### Cycle de vie du compte (modèle "ligne téléphonique")

Analogie : Nasoma fonctionne comme une ligne téléphonique prépayée africaine — vous ne rechargez pas, votre ligne est suspendue.

```
┌─────────────────────────────────────────────────────────┐
│ ACTIF       │ GRACE (30 jours)    │ GELÉ (>30j)         │
│ ────────────┼─────────────────────┼─────────────────────│
│ 100% des    │ Lecture seule       │ Pas d'accès direct  │
│ features    │ avec dernier OTP    │ Export RGPD sur     │
│             │ valable             │ demande uniquement  │
│             │ Paywall partout     │ Réactivation =      │
│             │                     │ nouveau ticket      │
└─────────────────────────────────────────────────────────┘
```

#### État ACTIF (crédit > 0 OU jours_restants > 0)
- Toutes les features : scan, session, profil, indicateurs, rapports, partage, examens blancs
- Streak + push hebdo + recommandations
- Login = phone + OTP courant (valable jusqu'à expiration du crédit)

#### État GRACE (J+0 à J+30 après expiration crédit)
- **Login phone + dernier OTP valide encore possible** (token "lecture seule")
- Lecture seule : historique scans, profil BKT figé, rapports passés, journal recommandations
- **Aucune nouvelle action** : pas de nouveau scan, pas de session, pas d'indicateur CT/MT/LT mis à jour
- Bannière permanente "Renouveler" + paywall partout

#### État GELÉ (J+31 et au-delà)
- Login direct **impossible** (dernier OTP expiré)
- Données **conservées** (corpus scans + profil BKT = Moat #1, ne pas supprimer)
- **Export RGPD sur demande** via support (email `dpo@nasoma.app`) — réponse < 30j (Art. 12 RGPD)
- **Réactivation** : acheter un nouveau ticket chez un vendeur → nouveau OTP → tout l'historique redevient accessible (les données n'ont jamais été supprimées)

#### État ARCHIVÉ (J+365 et au-delà)
- Compte transféré en stockage froid (Cloud Storage Coldline)
- Email parent à J+330 : "Voulez-vous garder vos données ? Réactivez avant le {date}. Sinon, anonymisation."
- Anonymisation effective à J+395 si aucune action — conformité RGPD Art. 5(1)(e) data minimisation

### Pourquoi cette mécanique est puissante

1. **Indépendance opérateurs** : zéro SMS récurrent. Renouvellement = ticket physique vendeur. Pas de défaillance réseau.
2. **Incitation au renouvellement maximale** : sans crédit, **aucune nouvelle valeur** ne se crée. Le profil BKT se fige, l'élève "perd ses jours de progression".
3. **Switching cost amplifié** : l'historique reste visible pendant 30j → le parent VOIT ce qu'il perd s'il ne renouvelle pas.
4. **Légalité préservée** : droit d'accès RGPD honoré (lecture 30j + export sur demande), droit à l'effacement honoré, infrastructure non pérennisée pour comptes morts.
5. **Anti-fraude renforcée** : OTP = preuve de paiement traçable jusqu'au vendeur. Si un compte abuse, on remonte au point de vente.

### Authentification — 2 flows distincts

#### Flow A — Premier accès (3 scans découverte gratuits)
**SMS OTP unique** (Firebase Phone Auth + Africa's Talking fallback) :
- Vérifie la propriété du numéro (anti-fraude critique en first-touch)
- Coût one-shot : ~0,02 $/inscription
- **Seul SMS de tout le cycle de vie du compte**
- Donne accès aux 3 scans / 7 jours

#### Flow B — Renouvellements + accès récurrent
**OTP ticket vendeur** (zéro SMS, zéro opérateur) :
- Vendeur saisit phone client → backend génère OTP → imprimé sur le ticket physique
- Client entre phone + OTP dans l'app → crédits activés + session ouverte
- Le **même geste** = paiement + auth + activation crédit

#### Message obligatoire sur chaque ticket physique

```
┌─────────────────────────────────────────────────┐
│ 🎟️ TICKET NASOMA — Plan {PLAN}                  │
│                                                 │
│ Numéro élève : +269 XX XX XX XX                 │
│ Code OTP     : 4 8 2 7 1 9                      │
│ Crédits      : 120 scans                        │
│ Valable      : 30 jours à compter de l'activation│
│                                                 │
│ ⚠️ GARDEZ CE TICKET PRÉCIEUSEMENT               │
│ Le code est votre clé d'accès à la plateforme   │
│ Sans le dernier code valable, vous perdez       │
│ l'accès à votre compte au bout de 30 jours.     │
│                                                 │
│ Acheté chez : Vendeur Nasoma #VND-0234          │
│ Le {DATE} à {HEURE}                             │
│ Hash sécurité : {HMAC8}                         │
└─────────────────────────────────────────────────┘
```

### La rotation OTP comme feature de sécurité

Chaque paiement génère un nouvel OTP qui remplace l'ancien dans la base. Cela signifie :

- **Le mot de passe change automatiquement** à chaque renouvellement (hebdo / mensuel)
- **Pas de "mot de passe permanent" qui traîne** dans la nature ou peut être deviné
- **Compromission d'un OTP = compromission limitée à la durée du crédit en cours** (24h / 7j / 30j max)
- **Vol de ticket = effet temporaire** (le compte sera reverrouillé au prochain renouvellement légitime)
- **Aucune base de données de mots de passe stockés en clair** — les OTP sont hashés SHA-256

C'est de la **rotation forcée** (équivalent NIST SP 800-63B mais piloté par l'usage produit, pas par une règle arbitraire). C'est plus sécurisé que la plupart des apps qui gardent un mot de passe haché pendant 10 ans.

### Tables Postgres (cf. architecture.md)

```sql
-- Comptes utilisateurs (extension de users)
ALTER TABLE users ADD COLUMN account_state VARCHAR(16) DEFAULT 'active';
-- 'active' | 'grace' | 'frozen' | 'archived'
ALTER TABLE users ADD COLUMN credit_expires_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN last_valid_otp_hash VARCHAR(128);
ALTER TABLE users ADD COLUMN last_valid_otp_expires_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN state_changed_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN first_signup_phone_verified BOOLEAN DEFAULT FALSE;
```

Cron quotidien à minuit local :
- Transition `active → grace` quand `credit_expires_at < NOW()`
- Transition `grace → frozen` quand `credit_expires_at + 30 days < NOW()`
- Transition `frozen → archived` quand `credit_expires_at + 365 days < NOW()`
- Email proactif à J+330 (warning anonymisation)

---

## 3 quinquies. Canal marketing permanent & SAV à deux tiers

> **Décision (2026-05-20) :** une application installée est un actif. Même si le service est suspendu (GRACE / FROZEN / ARCHIVÉ), un **canal marketing permanent** doit rester ouvert dans l'app. Le SAV humain est en revanche **réservé aux abonnés actifs**.

### Canal marketing permanent (tous états)

**Permanent et inconditionnel** — visible peu importe l'état du compte.

| Usage | Exemples |
|---|---|
| 📢 Promotions | "1 mois offert pour les anciens abonnés — code REVIENS" |
| 🆕 Mises à jour | "Nouveauté : examens blancs CEPE disponibles" |
| 🎓 Conseils éducatifs | "5 astuces pour préparer la rentrée" |
| 🔔 Annonces produit | "Nouvelle matière disponible : Anglais" |
| 💡 Re-engagement | "Tu as un compte Nasoma — viens voir ce qu'Ali a accompli" |

**Implémentation** :
- Écran `MarketingFeed` accessible depuis le menu, même en état GELÉ
- Push FCM possible vers comptes inactifs (re-engagement)
- **Aucune interaction requise** — lecture seule, taux d'engagement mesuré
- Garde l'app installée même quand le compte est suspendu = **base d'utilisateurs potentiels à réactiver**

### SAV à deux tiers — économie de ressources support

| État compte | IA Bot (Gemini Flash) | Escalade humaine |
|---|---|---|
| ACTIVE (abonné payant) | ✅ Réponse immédiate sur questions générales et techniques | ✅ Transfert vers agent humain si justifié (bug, problème complexe, plainte) |
| GRACE / FROZEN / ARCHIVÉ | ✅ Réponse IA sur questions générales uniquement (FAQ, comment réabonner, etc.) | ❌ **Pas d'agent humain** — économise les ressources |
| Non-abonné qui découvre l'app | ✅ IA pour orientation produit/marketing | ❌ |

#### Pourquoi cette logique
- Un abonné payant à 1 500 KMF/mois mérite un agent humain quand l'IA bloque
- Un compte gelé qui demande "comment je récupère mes données" → l'IA donne la procédure RGPD standard, pas besoin d'agent
- Économie estimée Y2 (50k users, dont 30% inactifs) : ~50 % du coût support humain

#### Workflow conversation
```
Utilisateur écrit un message
    ↓
IA Gemini Flash répond (avec contexte état compte)
    ↓
Si user pas satisfait → bouton "Parler à un humain"
    ├─ Si ACTIVE → ticket support créé, escalade
    └─ Si non-ACTIVE → message "Réactivez votre abonnement pour parler à un humain.
                       En attendant, [voici la FAQ] / [voici le PDF d'aide]."
```

#### Garde-fous IA SAV
- Modération Vertex AI Safety (déjà en place pour génération exercices)
- Pas de réponse sur sujets sensibles (santé, juridique) → orienter vers expert humain
- Logs structurés de toutes conversations pour audit RGPD
- Anonymisation des logs IA après 90 jours

### Tables Postgres (à coder Sprint 2.5)

```sql
-- Messages marketing (broadcast)
marketing_messages (
  id UUID PK, tenant_id UUID,
  title VARCHAR(120), body TEXT, cta_label VARCHAR(40), cta_url VARCHAR(240),
  audience VARCHAR(30),               -- 'all' | 'active' | 'inactive' | 'grace' | 'frozen' | 'plan:monthly'
  push_enabled BOOLEAN,                -- envoi push FCM auto à la publication
  starts_at TIMESTAMPTZ, ends_at TIMESTAMPTZ,
  language VARCHAR(10),                -- fr | en | sw | ar | shk
  priority SMALLINT,                   -- 1 (banner top) à 5 (feed bottom)
  created_by UUID, created_at TIMESTAMPTZ
)

-- Conversations SAV
support_conversations (
  id UUID PK, tenant_id UUID, user_id UUID,
  status VARCHAR(20),                  -- 'ai_only' | 'awaiting_human' | 'with_human' | 'closed'
  user_account_state VARCHAR(16),      -- snapshot état au moment de l'ouverture
  assigned_agent_id UUID,
  opened_at TIMESTAMPTZ, closed_at TIMESTAMPTZ,
  satisfaction_rating SMALLINT         -- 1-5 post-conversation
)

support_messages (
  id UUID PK, conversation_id UUID,
  sender_type VARCHAR(10),             -- 'user' | 'ai' | 'agent'
  sender_id UUID,
  content TEXT,
  ai_cost_usd NUMERIC(6,4),            -- pour BI coûts Gemini
  created_at TIMESTAMPTZ
)
```

### Endpoints API (à coder Sprint 2.5)

```
GET  /api/v1/marketing/feed             # accessible TOUS états (incl. frozen)
                                        # Returns: liste messages actifs filtrés audience

POST /api/v1/support/conversations      # ouvrir conversation
POST /api/v1/support/conversations/{id}/messages   # envoyer message
GET  /api/v1/support/conversations/{id}/messages   # poll messages

POST /api/v1/support/conversations/{id}/escalate   # demander humain
                                                   # → 200 si ACTIVE
                                                   # → 402 si non-ACTIVE avec
                                                   #     "Réactivez votre abonnement"
```

### Métriques business à suivre
- Taux d'ouverture marketing feed par état (active vs grace vs frozen)
- Taux de réactivation post-promo marketing
- Coût moyen support par ticket (active vs non-active)
- Satisfaction SAV par tier (IA vs humain)
- Conversion IA → humain (% des conversations escaladées chez ACTIVE)

---

## 3 sexies. Assistance vidéo payante & Dashboard vendeur

### Assistance vidéo payante (post-paid, ACTIVE only)

> Décision (2026-05-20) : assistance vidéo en ligne à **200 KMF / 10 min**, facturée à la prochaine recharge.

**Règles métier** :
1. Réservé aux comptes **ACTIVE** uniquement (vérifié au démarrage, refus 402 sinon)
2. **L'option GRATUITE doit toujours être présentée EN PREMIER** :
   > *"Une assistance gratuite est disponible auprès de votre vendeur agréé où vous achetez habituellement vos tickets."*

   L'app affiche les coordonnées + GPS du vendeur habituel **avant** d'évoquer l'option payante.
3. **Disclosure obligatoire** pour la session payante : tarif visible, consentement explicite (`user_consent=true`)
4. **Post-paid** : la dette est créée en `OutstandingBill`, prélevée par le vendeur à la prochaine recharge
5. Arrondi à la tranche de 10 min supérieure (8 min = 200 KMF, 12 min = 400 KMF)
6. Plafond session : 120 minutes (anti-runaway)

### Dashboard vendeur — outstanding bills

> Le vendeur DOIT voir les factures en attente AVANT toute transaction.

**Flow vendeur** :
```
1. Vendeur saisit le numéro client
2. GET /vendor/customers/{phone}/dashboard
   → snapshot : état compte + factures + plans dispos
3. Vendeur présente au client AVANT toute transaction :
   "Vous avez {N} factures en attente totalisant {X} KMF :
    - Assistance vidéo 20 min · 400 KMF
    Voulez-vous :
    [A] Régler les factures uniquement
    [B] Recharger un service uniquement
    [C] Les deux"
4. Client choisit → POST /vendor/recharge avec settle_bill_ids + new_plan
5. Backend règle factures + crée Payment + Subscription + OTP du ticket
6. Vendeur imprime le ticket avec OTP + rappel "GARDEZ CE TICKET"
```

### Diaspora purchase — vendeur proche de l'ENFANT par GPS

> Décision (2026-05-20) : pour les achats diaspora en ligne, recommander des vendeurs proches **de l'enfant**, pas du parent diaspora.

- Achat via portail diaspora (paiement Stripe/carte)
- OTP transmis au parent diaspora (qui l'envoie via WhatsApp à l'enfant)
- En plus, le backend retourne **jusqu'à 3 vendeurs proches du domicile de l'enfant** (utilise `users.home_latitude` / `home_longitude` / `home_city`)
- Cas d'usage : si l'enfant a besoin d'aide physique (caméra cassée, problème app), il peut se rendre chez l'un de ces vendeurs

Schéma `User` étendu avec champs `home_*` (consentement RGPD du parent).

### Sélection vendeur pour assistance — règle métier

1. **Premier choix** : le vendeur du dernier ticket de recharge acheté
2. **Si position GPS connue** ET ticket vendor > 10 km ET vendeur formé plus proche → recommander le plus proche par GPS
3. **Toujours afficher les deux options** dans l'app (primary + alternative)
4. Distance maximale "raisonnable" : 30 km (au-delà, retombe sur ticket vendor)

Calcul GPS : formule de Haversine (cf. `app/services/vendor_service.py`).

### Séparation des responsabilités AI / App

> Principe fondateur (2026-05-20) : **l'IA détecte, l'App décide.**

| Couche | Responsabilité | Exemple |
|---|---|---|
| **Backend (IA)** | Détecter le problème objectivement | `detection_type = HANDWRITING_ILLEGIBLE` confidence 0.42 |
| **Frontend (App)** | Décider du flow UX selon la détection + historique | Si 1ère fois : "Reprendre" ; si 2ème fois : modal contexte ; si récurrent : assistance |

L'enum `DetectionType` sert d'interface : SUCCESS, IMAGE_QUALITY_LOW, OCR_NO_TEXT, NO_SCHOOL_WORK, HANDWRITING_ILLEGIBLE, WRONG_PAGE, CONCEPT_MAPPING_FAILED, OCR_ERROR, NETWORK_ERROR.

---

## 3 septies. Canaux de communication & KYC (verrouillé 2026-05-20)

### Hiérarchie des canaux (économie maximale)

| Moment | Canal | Coût/msg | Raison |
|---|---|---|---|
| **1ère inscription** | WhatsApp Business | ~0,01 $ | Multimédia : vidéo onboarding 2min, images, liens |
| Renouvellements (app installée) | **Push FCM in-app** | 0 $ | Canal Nasoma gratuit |
| Marketing post-activation | In-app feed (tous états) | 0 $ | Lecture passive, sticky |
| Re-engagement (désinstall) | WhatsApp fallback | ~0,01 $ | Récupération possible |
| Fallback ultime | SMS Africa's Talking | 0,02 $ | Si WhatsApp indispo |

**Économie Y2 (50k users)** : ~3 750 $/mois vs 100 % SMS = **94 % d'économie**.

### Pré-check WhatsApp obligatoire en self-signup

> Décision (2026-05-20) : **avant tout envoi WhatsApp, l'app demande explicitement au user s'il a WhatsApp.**

**Pourquoi** :
1. Éviter les coûts API WhatsApp à perte (envoi à user sans WhatsApp)
2. Garantir un canal de relance pérenne (re-engagement, marketing, support)
3. Canaliser vers vendeur (Moat #3 distribution) les users sans WhatsApp

**Flow self-signup** :
```
1. Écran "S'inscrire"
2. PRÉ-CHECK : "As-tu un compte WhatsApp ?"
   ├─ [Oui] → POST /auth/signup/self → User créé + OTP WhatsApp envoyé
   └─ [Non] → écran "Pour activer Nasoma, tu as besoin de WhatsApp"
      ├─ Bouton "Installer WhatsApp" (Play Store deep link)
      ├─ Carte vendeur Nasoma le plus proche (GPS)
      └─ Suggère "Va voir Said au kiosque Mavingouni — il t'aidera à installer + activer en 5 min"
```

**Pas de SMS fallback à cette étape** — on ne se prive pas d'un canal de relance pérenne.

### KYC obligatoire au 1er signup (vendor + diaspora) — PAS dans l'app

> Décision (2026-05-20) : seule source de vérité d'identité = pièce scannée.
> **Le scan ID se fait UNIQUEMENT chez le vendeur ou via portail web diaspora.**
> **Jamais directement dans l'app mobile Android/iOS.**
>
> **Règle "1 seule pièce par compte = parent/tuteur"** : on n'exige PAS de pièce de l'enfant.
> C'est toujours le parent/tuteur (responsable légal) qui fournit sa propre CNI/passeport.
> Cela simplifie la compliance RGPD/COPPA mineurs et clarifie la chaîne de responsabilité.

| Source | Pièce requise | Status après upload |
|---|---|---|
| Vendor en personne | 1 pièce du parent/tuteur (CNI/passeport) | **verified** auto (vendeur = preuve IRL) |
| Diaspora portal (web, hors store) | 1 pièce du parent/tuteur (CNI/passeport) | **pending** (review admin) |
| Self-signup app | Aucune | **not_verified** (opérations sensibles bloquées) |

#### Champs `guardian_*` capturés au signup
- `guardian_full_name` : nom complet du parent/tuteur
- `guardian_document_type` : `cni` ou `passport`
- `guardian_relationship` : `parent` / `tuteur` / `famille_proche`
- `guardian_id_image` : upload multipart (image recto ou recto-verso)

Stocké dans `IdentityDocument.extracted_name` + `image_storage_key` (chiffré KMS).

#### Pourquoi PAS dans l'app mobile (Google Play / Apple App Store)

| Contrainte store | Impact | Mitigation choisie |
|---|---|---|
| Designed for Families : interdit collecte PII mineurs sans consent parental horodaté | App rejetée si on collecte ID enfant | KYC fait par parent au portail diaspora (web) |
| Sensitive data policy : ID = catégorie sensible | Data Safety Form + Privacy Policy stricte + review 2-4 semaines | Pas de collecte ID dans app → review fluide |
| Risque suspension app | Si plainte parent ou audit Google | Zéro collecte ID dans app = zéro risque |
| Apple App Store encore plus strict | iOS Y2 bloqué si on dépend du scan in-app | Vendor flow = même code, indépendant du store |

#### Bénéfices stratégiques de ce choix

1. **Compliance immédiate Google Play + Apple App Store** : zéro friction review, lancement rapide
2. **Renforce Moat #3 (distribution physique)** : le client DOIT visiter un vendeur pour passer en payant → sticky, relation, conversion
3. **Qualité données supérieure** : vendeur vérifie humain en face, pas une photo de photo
4. **Délai mise en marché** : pas d'attente review sensitive data
5. **Coût intégration nul** : pas de ML Kit Document Scanner à intégrer, pas d'écrans, pas de tests
6. **Sécurité** : pas de risque de rétention d'images ID sur device user

#### Conséquence UX pour self-signup

Quand un user self-signup épuise ses 3 scans gratuits, l'app affiche :

```
🎟️ Tes scans gratuits sont terminés !

Pour continuer, achète un ticket Nasoma chez un vendeur.

Le vendeur va aussi t'aider à finaliser ton compte
en scannant ta pièce d'identité (étape obligatoire pour
les paiements).

[Trouver un vendeur près de moi]   ← affiche carte GPS

Pas de vendeur dans ton quartier ? Demande à un proche
qui voyage en France ou aux Émirats de payer pour toi
via notre site web.
```

Stockage : Cloud Storage **chiffré KMS** (AES-256-GCM). Rétention : 5 ans après dernier usage.

Sans pièce, opérations sensibles refusées :
- Paiement diaspora bloqué
- Assistance vidéo refusée
- Track A si jamais réintroduit

### Endpoints
- `POST /vendor/customers/signup` (multipart : pièce + form data)
- `POST /diaspora/customers/signup-and-purchase` (multipart : 2 pièces + form)
- `POST /auth/signup/self` (avec pré-check WhatsApp obligatoire)
- Subsequent : `/diaspora/purchase` (push FCM) ou `/vendor/recharge` (ticket physique)

---

## 3 ter. Rétention pluriannuelle — l'arme nucléaire

### L'effet CM1 → 3ᵉ (7 ans)
Un enfant qui commence Nasoma en **CM1** et reste jusqu'en **3ᵉ** = **7 ans d'usage**.

**LTV potentielle** : 1 500 KMF × 12 × 7 = **126 000 KMF** (~252 €) par enfant.
Avec une famille de 3 enfants espacés de 2 ans : **378 000 KMF** (~756 €) sur 9 ans.

### Pourquoi c'est défendable
- **Le livret scolaire numérique permanent** : 7 ans d'historique BKT + scans + bulletins (mensuels) — c'est l'équivalent d'un dossier médical pédagogique.
- **Préparation aux examens nationaux** : Nasoma s'aligne progressivement vers CEPE (fin primaire) puis BEPC (fin collège) avec entraînements spécifiques.
- **Réseau cohérent** : le parent qui a 3 enfants et 6 ans de Nasoma ne migrera jamais.
- **Switching cost émotionnel** : "Ali a son journal sur Nasoma depuis qu'il est en CM1" — c'est psychologiquement irremplaçable.

### Action stratégique
**Communiquer dès l'onboarding** : "Avec Nasoma, suis Ali de la CM1 jusqu'au BEPC — son dossier pédagogique le suit pour la vie."

---

## 4. Synthèse — Hiérarchie des moats

| Moat | Force | Délai construction | Coût Google pour battre |
|---|---|---|---|
| **#1 BKT longitudinal + corpus scans + indicateurs CT/MT/LT** | 🟢 Très élevée | Immédiat + s'enrichit dans le temps | Très élevé — exige fidélité 6+ mois |
| **#2 Knowledge Graph APC_KM validé CIPR** | 🟡 Moyenne | 3-6 mois | Faible — Google peut générer si motivé |
| **#3 Distribution physique + paiement local** | 🟢 Élevée | 3 mois (réseau écoles) | Très élevé — pas de ROI Google sur 800k habitants |
| **#4 Canal in-app + push FCM (habitude)** | 🟢 Élevée | 6 mois d'usage | Très élevé — habitude difficile à déloger |
| **#5 Partenariats institutionnels** | 🔴 À construire | 12-18 mois | Élevé — relations locales |
| **#6 Méthode pédagogique propriétaire (Spaced Repetition + Examens blancs)** | 🟢 Très élevée | 3 mois (Sprint 2) | Très élevé — exige KG validé + BKT mature |
| **#7 Réseau social parents + diaspora** | 🟢 Élevée | 6 mois (effet réseau) | Très élevé — ancrage culturel local |

**Conclusion stratégique** : la défense crédible 18 mois repose sur **#1 (BKT + corpus scans)**, **#3 (distribution)**, **#6 (méthode propriétaire)** et **#7 (réseau parents)**. Ces 4 moats doivent être **prioritaires absolus** dans l'exécution.

### Loi de la composition des moats
Aucun moat seul n'est suffisant. **C'est leur empilement qui crée l'effet :**

> Un élève qui utilise Nasoma 3 fois/semaine pendant 12 mois accumule :
> 150 scans archivés + profil BKT précis sur 150 concepts + 50 rapports SMS dimanche + 3 examens blancs + un parrainage à un cousin + un livret scolaire de 12 mois.
> **C'est cet empilement qui rend la migration vers Gemini émotionnellement et pratiquement impossible.**

---

## 5. Playbook défensif anti-Google (12 mois)

### Phase 1 (juin-août 2026) — Pilote 200-500 élèves
- ✅ Lancer le BKT dès Sprint 1 (Moat #1)
- ✅ Mettre en place le **corpus de scans archivés** dès le 1ᵉʳ scan
- ✅ Imprimer et distribuer 5 000 tickets de recharge dans 3 écoles partenaires
- ✅ Lancer l'**écran "Rapport hebdo" in-app + push FCM dimanche 19h** dès le premier mois (Moat #4)
- ✅ Coder les **boucles d'engagement** (streak, cascade rappels) — Sprint 2
- ⚠️ Approcher 3 inspecteurs CIPR pour valider le KG (Moat #2)

### Phase 2 (sept-déc 2026) — Croissance Comores
- Étendre à 10 écoles privées Moroni + Mutsamudu
- Activer le **code de parrainage** (Moat #7)
- Lancer la **fonctionnalité partage WhatsApp** rapport hebdo (acquisition virale)
- Lancer le **canal diaspora** (Facebook ads France ciblées Comoriens-de-France)
- Recruter 5 ambassadeurs parents par école (commissions)
- Coder **Spaced Repetition** + 1ᵉʳ **examen blanc** trimestriel (Moat #6)

### Phase 3 (jan-juin 2027) — Verrouillage institutionnel
- Signature LOI avec Ministère Éducation Nationale (Moat #5)
- Reconnaissance officielle KG par CIPR (Moat #2 finalisé)
- Lancement co-financé UNICEF/AFD
- **Lancement officiel "Livret scolaire Nasoma 7 ans"** (rétention pluriannuelle)

### Anti-pattern à éviter
- ❌ Ne PAS communiquer sur "IA Vision corrige tes copies" — c'est Google.
- ❌ Ne PAS développer Track A (notes/présence) — c'est un autre marché, ça dilue.
- ❌ Ne PAS essayer d'être multi-pays trop tôt — la profondeur Comores > l'expansion superficielle.
- ❌ Ne PAS supprimer les anciens scans pour économiser le stockage — ils sont l'actif Moat #1.
- ❌ Ne PAS faire de gamification toxique (loot box, classement public élèves) — risque réglementaire mineurs.

---

## 6. Honnêteté radicale — ce que Nasoma N'A PAS encore

| Item | Réalité au 2026-05-20 |
|---|---|
| Partenariats institutionnels | ❌ Aucun signé |
| Validation pédagogique CIPR | ❌ Pas encore obtenue |
| 200-500 élèves pilote | ❌ À recruter |
| Knowledge Graph 650 concepts | ⚠️ Squelette créé, 99 % à remplir |
| APK testable | ❌ Scaffolding seulement |
| Intégration Hollo Money | ⚠️ Doc à demander au provider |
| Code de production | ⚠️ Sprint 1 pas démarré |
| 1ʳᵉ vente | ❌ |

**Le moat existe sur le papier — il devra être construit dans les 12 mois.**
La fenêtre est étroite avant que Google sorte un "Gemini Tutor Africa" générique.

---

## 7. Mantra stratégique (à imprimer)

> **Gemini corrige une copie.**
> **Nasoma construit un élève.**
>
> Gemini = outil ponctuel.
> Nasoma = relation longitudinale.
>
> Gemini = global, gratuit, anonyme.
> Nasoma = local, payant, ancré.

---

*Document à relire à chaque revue trimestrielle. Mise à jour : 2026-05-20.*
*CK Innovation SARL — ABDU LKADER Mohamed Amound.*
