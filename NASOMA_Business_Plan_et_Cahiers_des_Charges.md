# NASOMA
## Business Plan Détaillé & Cahiers des Charges Fonctionnel et Technique

> **Document de référence pour le développement du MVP Android par IA de codage (Claude Code, Kimi K2, emergent.sh, Cursor, etc.)**

**Version :** 1.0 — Mai 2026
**Porteur du projet :** CK INNOVATION (Moroni, Union des Comores)
**Statut :** Confidentiel — Document destiné au développement technique

---

## TABLE DES MATIÈRES

**PARTIE I — BUSINESS PLAN**
1. Executive Summary
2. Vision, Mission & Valeurs
3. Le Problème : Le Constat d'Urgence
4. La Solution : Nasoma — L'IA Préventive
5. Analyse du Marché
6. Analyse Concurrentielle & Positionnement
7. Modèle Économique & Pricing
8. Stratégie Go-to-Market & Acquisition
9. Roadmap Stratégique (POC → MVP → Scale)
10. Projections Financières Y1-Y3
11. Équipe & Organisation
12. Risques & Mitigation

**PARTIE II — CAHIER DES CHARGES FONCTIONNEL**
13. Personas & Cas d'Usage
14. User Stories (par persona)
15. Spécifications Fonctionnelles Détaillées
16. Parcours Utilisateur (User Flows)
17. Wireframes & Écrans (Spécifications)
18. Règles Métier
19. Critères d'Acceptation MVP

**PARTIE III — CAHIER DES CHARGES TECHNIQUE**
20. Architecture Générale
21. Stack Technologique
22. Modèle de Données (Schémas BDD)
23. Spécifications API (REST)
24. Pipeline IA Vision & OCR
25. Moteur Adaptatif (Bayesian Knowledge Tracing)
26. Sécurité & Conformité
27. DevOps & Infrastructure
28. Plan de Tests
29. Instructions de Build (Step-by-Step pour IA codeuse)

---

# PARTIE I — BUSINESS PLAN

## 1. EXECUTIVE SUMMARY

**Nasoma** (du swahili « moi, j'étudie » — « ni-na-soma ») est une plateforme EdTech préventive propulsée par l'Intelligence Artificielle, conçue pour le marché africain. Elle rompt avec la révision passive de fin de trimestre en proposant un **outil d'intervention chirurgicale quotidienne** qui intercepte l'incompréhension d'un élève avant qu'elle ne devienne une lacune définitive.

### Le Pitch en une phrase
> **Nasoma tue la lacune dans l'œuf, jour après jour, devoir après devoir.**

### Filiation : du projet LISEC / SOMA à Nasoma

Nasoma s'inscrit dans la continuité directe d'un projet historique porté par **CK INNOVATION** (Moroni, Comores) depuis 2018 :
- **2018 — Projet LISEC** (Livret Scolaire Unique Numérique Sécurisé). Projet présenté au Commissariat à l'Éducation de Ngazidja pour le suivi du parcours élèves via SMS et carte RFID. Potentiel marché chiffré dès 2018 : **723 840 000 KMF/an** (~1,47 M €) au plan national comorien, soit **3,6 Mds KMF (~7,36 M €) sur 5 ans** — base 160 000 élèves de l'élémentaire et du secondaire + 14 000 universitaires.
- **2024 — Projet SOMA** : évolution vers une plateforme régionale de collecte, traitement et sécurisation des données du système éducatif comorien et de la zone océan Indien (cf. NDA CK Innovation 2024). Cible : tous les enfants des écoles élémentaires, collèges et lycées du CP à la Terminale.
- **2026 — Nasoma** : pivot stratégique vers l'IA Vision générative et l'EdTech préventive grand public — la marque consommateur du projet, avec une cible Pan-Afrique.

Ce passé est un actif majeur : réseau institutionnel comorien établi (Commissariat à l'Éducation de Ngazidja, Mairies, écoles privées, ARAB SOFT, ANACM, AMPSI, Ministère de l'Intérieur, ORTC), connaissance fine du terrain, et données de marché propriétaires.

### Le Workflow Cœur — Le « Scan-Rattrapage »
```
[Devoir corrigé en classe] → [Scan smartphone] → [Extraction IA des erreurs]
       → [Diagnostic chirurgical] → [Pack de rattrapage flash : 3-4 micro-exercices ciblés]
```

### Chiffres Clés du Marché
- **TAM 2030 :** 400 millions d'élèves en Afrique
- **SAM EdTech Afrique 2030 :** 20 milliards USD
- **Cible interne 2030 :** 5 millions d'utilisateurs actifs

### Projections Financières Synthétiques
| Année | Utilisateurs | ARR | Jalon |
|-------|-------------|-----|-------|
| Y1 | 50 000 | 500 000 $ | Product-Market Fit |
| Y2 | 250 000 | 2,5 M $ | Expansion géographique |
| Y3 | 1 000 000 | 10 M $ | Leadership Afrique |

**Break-even :** Mois 18 post-lancement commercial.

### Vision 2030
> Équiper 50 millions d'élèves africains d'un tuteur IA personnel pour que plus aucun enfant ne soit laissé pour compte.

---

## 2. VISION, MISSION & VALEURS

### Vision
Faire en sorte qu'aucun élève africain ne termine sa journée scolaire sur une incompréhension non traitée.

### Mission
Mettre dans la main de chaque famille africaine un tuteur IA accessible, personnalisé et aligné aux curriculums nationaux, capable de transformer chaque échec quotidien en victoire pédagogique.

### Valeurs
- **Préventif > Curatif** : agir sur la cause (la lacune du jour), pas le symptôme (l'échec à l'examen).
- **Frugal et accessible** : fonctionne sur Android entrée de gamme, en mode offline-first, sur réseau 2G/3G.
- **Souveraineté éducative** : alignement strict sur les curriculums nationaux (CBC, NECTA, RDC, Comores).
- **Souveraineté des données** : hébergement et traitement locaux, conformité Data Protection Act / NDPR.
- **Confiance parentale** : transparence absolue sur l'apprentissage de l'enfant.

---

## 3. LE PROBLÈME : LE CONSTAT D'URGENCE

### La Pauvreté d'Apprentissage en Afrique : un chiffre choc

> **86 % des enfants africains ne maîtrisent pas la lecture à 10 ans** (Banque Mondiale — Learning Poverty 2022).

Ce n'est pas un problème d'accès à l'école : c'est un problème de **qualité quotidienne** des apprentissages.

### L'effet domino : pourquoi l'incompréhension du lundi devient un échec définitif

Une **incompréhension non corrigée le lundi devient un blocage définitif au bout d'un mois**. Quelques exemples concrets :
- Un élève qui ne comprend pas la **retenue** en mai sera bloqué sur les **fractions** en septembre, puis sur les **pourcentages** en mars.
- Un élève qui ne saisit pas l'**accord du verbe avec le sujet** s'effondrera ensuite sur l'analyse grammaticale puis sur la rédaction.

Aucun mécanisme courant ne détecte ce blocage **le soir même**.

### La surcharge structurelle des classes africaines

- **Moyenne 50+ élèves par classe** en Afrique subsaharienne. Aux Comores : **62 élèves par salle de classe en moyenne** (PASEC 2010), **27 élèves par enseignant**.
- **Moins de 40 %** des élèves comoriens sont **assis confortablement** en classe.
- **Moins de 42 %** des élèves utilisent les manuels de français et de mathématiques en classe.
- **Seulement 8,7 %** des écoles primaires comoriennes disposent d'une bibliothèque ; **0,8 %** d'une salle informatique ; **26 %** de l'électricité.

Dans ce contexte, l'enseignant ne peut tout simplement plus diagnostiquer les lacunes individuelles. Le système est structurellement incapable de fournir un suivi personnalisé.

### Les Comores en 2025 : un cas d'école

D'après les données réelles du Gouvernorat de Ngazidja et les rapports nationaux récents :
- **Taux réel de réussite à l'entrée en 6e : ~18 %**
- **Taux réel de réussite au BEPC : ~15 %**
- **Taux réel de réussite au Baccalauréat : ~7 %**
- **41 % des élèves de 5ᵉ année** ont un score inférieur à 25/100 en français (PASEC).
- **30 % des élèves de 5ᵉ année** ont un score inférieur à 25/100 en mathématiques (PASEC).
- **50 % des élèves** inscrits en 1ʳᵉ année du primaire **n'atteignent pas la 6ᵉ année** (Banque Mondiale).
- **Redoublement : 26 à 31 %** par année d'études — soit un **gaspillage massif** des ressources publiques.

### Pourquoi le système actuel crée des échecs programmés

**a) La lacune quotidienne s'accumule.** Aucun mécanisme courant ne détecte le blocage **le soir même**.

**b) La révision est réactive.** Les outils existants (PDF d'annales, manuels scolaires, vidéos YouTube) se déclenchent à 2 semaines de l'examen — c'est trop tard.

**c) Les parents sont aveugles.** Ils voient une note (12/20) mais ignorent la nature exacte du blocage. **Beaucoup sont eux-mêmes peu alphabétisés** (en 5ᵉ année comorienne, le PASEC mesure l'analphabétisme parental comme facteur explicatif majeur de l'échec).

**d) Le tutorat privé est élitiste.** Les répétiteurs coûtent 30-100 $/mois — inaccessible à la classe moyenne.

**e) Les EdTech occidentales (Khan Academy, Coursera) sont hors-curriculum.** Elles ne suivent pas les programmes nationaux CBC (Kenya), NECTA (Tanzanie), curriculum comorien APC, RDC, etc.

**f) Le numérique scolaire est embryonnaire.** Aux Comores, en dehors de Moroni, **aucune école n'a de salle informatique fonctionnelle**. Les TIC en éducation restent une promesse non tenue depuis le colloque #ComoresTICE de 2018.

### Le diagnostic PASEC : les vrais leviers d'amélioration

Le PASEC 2010 a identifié les facteurs ayant un impact significatif sur les acquisitions scolaires. **Nasoma cible directement les leviers actionnables au niveau famille / élève** :
- ✅ La diminution du **redoublement** au profit d'un meilleur suivi pédagogique de l'élève
- ✅ Une plus grande **utilisation des manuels** en classe et à la maison
- ✅ L'**aide aux devoirs à la maison** (impact PASEC démontré)
- ✅ Le respect de la **couverture du programme scolaire**
- ✅ La **diminution du travail des enfants** hors travail scolaire
- ✅ L'**alphabétisation des parents** (que Nasoma compense par l'IA vocale + rapports SMS adaptés)

### Conséquences mesurables
- Taux de redoublement élevé.
- Décrochage scolaire massif au passage primaire-secondaire (50 % des élèves comoriens n'atteignent pas la 6ᵉ année).
- Anxiété de performance des parents en pleine croissance économique.
- Perte économique pour les États : recommencer l'enseignement d'un élève coûte ~100 $/an en RNB comorien (revenu national brut/habitant ~750 $) — soit 13 % du revenu par habitant.

---

## 4. LA SOLUTION : NASOMA — L'IA PRÉVENTIVE

### Positionnement
**« Le Traqueur Quotidien de Lacunes »**

### La Boucle de Succès Nasoma (3 étapes)

**1. COLLECTE — Le Scan**
L'élève (ou le parent) photographie chaque soir avec son smartphone la copie du devoir corrigé, ou un exercice du jour en cours.

**2. DIAGNOSTIC — L'IA Vision**
L'IA analyse trois choses simultanément :
- la **note** finale (signal du résultat global) ;
- les **ratures de l'élève** (signal de doute, de réessais) ;
- les **annotations rouges du professeur** (signal d'erreur localisée) ;
- les **patterns d'erreur** (oubli de retenue, inversion de signe, faute d'accord, confusion conceptuelle, etc.).

Elle localise précisément la **rupture de logique** — par exemple « blocage exact sur la retenue à l'exercice 4 » — et met à jour le **Profil de Compétence** de l'élève (Knowledge Graph).

**3. RATTRAPAGE — La Remédiation Flash**
Génération instantanée sur l'écran d'un **pack de 3 à 4 micro-exercices interactifs** ciblés sur la brique manquante. Pas de cours long, juste une correction neuronale à chaud — terminée avant le coucher.

### Le « WOW » Produit
Chaque soir, le parent voit l'application transformer un échec scolaire de l'après-midi en une victoire à la maison. L'enfant s'écrie : **« Nasoma ! »** (« j'étudie ! / j'ai compris ! »).

### Storytelling Émotionnel
La promesse n'est plus *« Révise pour ton examen »* mais :
> **« Ne laisse aucune journée se terminer sur une incompréhension. »**

### Mascotte
**Mimi, Nasoma.** Mimi signifie « moi » en swahili. Slogan : *« Moi, j'étudie. »*

---

## 5. ANALYSE DU MARCHÉ

### TAM / SAM / SOM

| Indicateur | Volume | Source |
|-----------|--------|--------|
| **TAM** (Total Addressable Market) | 400 M élèves Afrique 2030 | UNESCO / Banque Mondiale |
| **SAM** (Serviceable Available Market) | 20 Mds USD EdTech Afrique 2030 | HolonIQ |
| **SOM Y3** (Serviceable Obtainable Market) | 1 M users / 10 M $ ARR | Projections internes |

### Zoom marché Comores (marché pilote)

**Données système éducatif comorien (sources : Ministère de l'Éducation, DGPEP, PASEC 2010, recensements communaux) :**

- **Population scolaire totale ciblée** : ~160 000 élèves (élémentaire + secondaire) sur les 3 îles (Ngazidja + Ndzuwani + Mwali) + ~14 000 universitaires UDC = **~174 000 utilisateurs potentiels directs**.
- **Découpage administratif scolaire** : **17 Circonscriptions d'Inspection Pédagogique Régionale (CIPR)** — 2 à Mwali, 5 à Ndzuwani, 10 à Ngazidja.
- **Établissements** :
  - **Collèges publics** : 47 (6 Mwali + 14 Ndzuwani + 27 Ngazidja).
  - **Collèges privés** : 89 (4 Mwali + 27 Ndzuwani + 58 Ngazidja).
  - **Lycées publics** : 10 (1 Mwali + 5 Ndzuwani + 4 Ngazidja).
  - **Lycées privés** : 62 (2 Mwali + 17 Ndzuwani + 43 Ngazidja).
  - **Total écoles secondaires** : 208 établissements (151 privés / 57 publics).

**Implication stratégique :** la cible **B2B écoles privées comoriennes** est composée de **151 collèges/lycées privés** — un terrain de jeu accessible (concurrence sur l'image, parents payeurs présents). Les écoles privées du secondaire ont un fort intérêt à se différencier par un outil digital crédible.

**Marché monétisable Comores (modèle SMS de base, projection LISEC 2018 confirmée par le marché) :**
- **Service quotidien (notes/présence) :** ~723 M KMF/an net (~1,47 M €/an) à plein régime national.
- **Service annuel (inscription/licence) :** ~1,12 Mds KMF (~2,28 M €) au démarrage.
- **Potentiel cumulé 5 ans :** ~4,2 Mds KMF (~8,6 M €).

Ces chiffres sont **conservateurs** : ils ne prennent pas en compte les abonnements premium IA générative que Nasoma ajoute.

### Pays Cibles Prioritaires (par vague)

**Vague 1 — Pilote (Y1) :**
- 🇰🇲 Union des Comores (marché-test, siège CK Innovation, réseau institutionnel établi depuis 2018)
- 🇹🇿 Tanzanie (curriculum NECTA, swahilophone, proximité culturelle Comores)
- 🇰🇪 Kenya (curriculum CBC, anglophone, classe moyenne dynamique)

**Vague 2 — Expansion (Y2) :**
- 🇨🇩 RDC (francophone, énorme bassin d'élèves)
- 🇷🇼 Rwanda
- 🇺🇬 Ouganda
- 🇲🇬 Madagascar (proximité géographique, océan Indien)

**Vague 3 — Scale (Y3+) :**
- 🇸🇳 Sénégal, 🇨🇮 Côte d'Ivoire, 🇨🇲 Cameroun, 🇳🇬 Nigeria

### Drivers de Marché
- 400 M+ utilisateurs de smartphones en Afrique (en croissance).
- Classe moyenne émergente priorisant la réussite scolaire au-dessus de toute autre dépense discrétionnaire.
- Pénétration Mobile Money (M-Pesa, Orange Money, Airtel Money, Mvola, Hollo, Huri Money) supérieure à 70 % dans plusieurs marchés cibles.
- Aux Comores spécifiquement : **Hollo (Comores Telecom)** et **Mvola (Telma)** sont les deux acteurs majeurs ; SMS à coût bas négociable (~1 KMF/SMS via opérateurs nationaux historiques, ~0,01 € via opérateurs internationaux type 1s2u.com).
- Réseaux 4G en déploiement, fallback 2G/3G encore nécessaire.
- **Tendance forte : décentralisation éducative**. Aux Comores, depuis 2017, **l'éducation de base est transférée aux Communes** (note du Commissariat à l'Éducation de Ngazidja, 23 août 2017) — 54 communes deviennent des décideurs clés pour le numérique scolaire, ouvrant un canal B2G original.

### Cible Démographique Précise
- **Élèves :** 8-18 ans, du CP à la Terminale (équivalent local).
- **Parents :** 28-55 ans, urbains et péri-urbains, smartphone Android, classe moyenne émergente, à minimum 1 actif salarié dans le foyer.
- **Écoles privées :** établissements 100-2000 élèves (208 écoles secondaires aux Comores, dont 151 privées).
- **Diaspora comorienne** : ~300 000 personnes (France, Mayotte, Madagascar, EAU), à fort pouvoir d'achat, finance les études des enfants/neveux/nièces restés au pays — **payeur indirect majeur souvent oublié** par les acteurs locaux.

### Ancrage institutionnel et partenariats potentiels (Comores)
- **Commissariat à l'Éducation de Ngazidja** : interlocuteur déjà engagé (échanges 2018 et NDA 2024).
- **Ministère de l'Éducation Nationale comorien**.
- **CIPR (17)** : relais opérationnel terrain.
- **Mairies (54)** : depuis 2017, gestion administrative directe des écoles primaires publiques.
- **Université des Comores (UDC)** : extension marché Y2.
- **Partenariat Mondial pour l'Éducation (PME)** + UE + UNICEF + AFD : bailleurs susceptibles de cofinancer une licence sociale (zero-rating, sponsoring zones rurales pauvres).
- **Ambassade de France** : agence de coordination PME, intérêt explicite à soutenir l'innovation EdTech crédible et alignée curriculum (cf. discours 11ᵉ Conférence Nationale).

---

## 6. ANALYSE CONCURRENTIELLE & POSITIONNEMENT

### Matrice Concurrentielle

| Acteur | Type d'offre | Faiblesse |
|--------|-------------|-----------|
| **Apps de Past Papers** (Snapplify, etc.) | PDF d'annales statiques | Passif / pas d'IA / pas de remédiation |
| **Khan Academy / Coursera / Brilliant** | Cours vidéo internationaux | **Hors curriculum local** (CBC, NECTA, RDC…) |
| **Eneza Education / uLesson / Foondamate** | Quiz + chat WhatsApp | Pas de scan de copie, pas de diagnostic des **erreurs personnelles** |
| **Répétiteurs privés** | Tutorat humain | Élitiste, coûteux (30-100 $/mois), pas scalable |
| **NASOMA** | **IA adaptative basée sur les erreurs réelles du jour** | — |

### Avantage Compétitif Soutenable (Moat)

**Nasoma est le seul acteur traitant la cause racine — la lacune quotidienne — plutôt que le symptôme — l'échec à l'examen.**

**Les 5 piliers du moat :**
1. **Knowledge Graph propriétaire** : 5 000+ micro-concepts alignés sur les curriculums nationaux (CBC, NECTA, RDC, Comores).
2. **Données comportementales propriétaires** : chaque scan enrichit le modèle (network effect, defensible data moat).
3. **OCR optimisé écriture manuscrite africaine** : modèle fine-tuné sur les cahiers d'écoliers locaux (avant-papier important).
4. **Distribution scolaire B2B2C** : partenariats directeurs d'écoles → effet de levier viral.
5. **Mode offline-first sur Android low-end** : aucun concurrent global n'investit dans ce niveau de frugalité réseau.

---

## 7. MODÈLE ÉCONOMIQUE & PRICING

### Modèle Hybride à 4 Segments

| Segment | Offre | Prix Estimé | Notes |
|---------|-------|-------------|-------|
| **B2C Lite** (free tier) | Scan illimité + diagnostic basique | Gratuit (Ad-supported) | Acquisition / traction / lead generation |
| **B2C Pro** | Exercices personnalisés + IA Vocale + rapport | **1,50 $ / semaine** | Cœur de la monétisation |
| **B2C Family** | Jusqu'à 4 profils enfants + rapport hebdo parent par SMS | **4,00 $ / mois** | Maximisation ARPU famille |
| **B2B Écoles** | Licence annuelle par élève | **10,00 $ / an** | Volume + intégration officielle |
| **Partenariats Telcos** | Sponsoring zero-rating data | Variable | Levier de distribution massive |

### Stratégie de Tier Pricing — Logique

- **Le scan reste gratuit, toujours.** C'est l'acte de captation : il génère le profil de compétence.
- **La remédiation premium se paye.** L'IA vocale, l'expérience adaptative profonde, les rapports parentaux SMS sont les value-add monétisés.
- **Renouvellement mode automatique** par défaut (avec opt-out), pour maximiser LTV.
- **Achats à la semaine** (ticket d'entrée 1,50 $) car la classe moyenne africaine paie souvent en semainier (logique des recharges mobiles).

### Modes d'Encaissement

| Canal | Avantage | Usage prioritaire |
|-------|----------|-------------------|
| **Mobile Money** (M-Pesa, Orange Money, Airtel Money, Mvola, Hollo, Huri) | Pénétration > 70 % en Afrique de l'Est | **Canal #1** |
| **Ticket de recharge revendeurs écoles** | Distribution physique scolaire (modèle Senelec/orange recharges) | Bootstrap Y1 |
| **Carte bancaire** (Stripe, Flutterwave, Paystack) | Diaspora payante pour enfants restés au pays | Croissant Y2 |
| **Prélèvement automatique bancaire** | Fidélisation classe moyenne haute | Optionnel |

### KPIs Financiers Cibles
- **LTV / CAC ratio :** 4:1 (cible)
- **CAC :** < 2,50 $ (acquisition via bouche-à-oreille parental « Mimi, Nasoma »)
- **Churn mensuel :** < 8 %
- **Conversion freemium → premium :** > 12 %

---

## 8. STRATÉGIE GO-TO-MARKET & ACQUISITION

### Acquisition Virale — 3 Canaux

**Canal 1 : WhatsApp Bot (point d'entrée gratuit)**
- Un bot WhatsApp officiel Nasoma propose un « diagnostic gratuit » : le parent envoie une photo de copie, reçoit instantanément l'analyse + le lien d'installation.
- Effet viral : le parent partage automatiquement l'analyse dans le groupe WhatsApp des parents de la classe.

**Canal 2 : Ambassadeurs Écoles**
- Partenariats directs avec les directeurs d'écoles privées comoriennes, kenyanes, tanzaniennes.
- L'école intègre Nasoma comme **outil officiel de suivi** des devoirs maison.
- Modèle : ticket de recharge en gros vendus par l'école aux familles (commission école 10-15 %).

**Canal 3 : Bouche-à-oreille parental (« Mimi, Nasoma »)**
- Slogan viral conçu pour être prononcé par l'enfant lui-même.
- Campagnes radio locales + SMS push via Comores Telecom / Telma (~1 KMF/SMS).

### Funnel d'Acquisition

```
SMS / WhatsApp Bot  →  Diagnostic gratuit
        ↓
Installation app + Activation OTP (mail + SMS, type WhatsApp)
        ↓
Free tier — Onboarding 3 minutes — Premier scan
        ↓
Engagement quotidien — Streak — Notifications push
        ↓
Conversion → Pro 1,50 $/sem OU Family 4 $/mois
```

### Activation OTP & KYC Léger
Sécurisation par OTP envoyé par SMS (et email) lors du premier scan — modèle WhatsApp. Alimente une base CRM marketing fiable.

---

## 9. ROADMAP STRATÉGIQUE (POC → MVP → SCALE)

### Approche en 2 vitesses : « Tracks parallèles »

Le projet exploite deux tracks pour minimiser le risque et maximiser la traction :

| Track | Nature | Délai mise en marché | Source revenus |
|-------|--------|----------------------|----------------|
| **Track A — « Suivi temps réel »** | Continuité directe LISEC : présence/absence + notes en temps réel via SMS et appli légère | **3-6 mois** (faible complexité technique) | Bootstrap revenus dès Q1 |
| **Track B — « Scan-Rattrapage IA »** | Cœur produit Nasoma : IA Vision + remédiation flash | 6-12 mois (R&D IA) | Pricing premium |

Les deux tracks **partagent la même appli** et la même base utilisateurs — le Track A nourrit l'IA du Track B (données comportementales).

### Phase 0 — POC (Proof of Concept) | Mois 1-3
**Objectif : *Can we build it ?***

- Validation faisabilité OCR sur copies d'écoliers comoriens/kenyans (corpus 1 000 copies).
- Test pipeline : Google Vision API ou Claude Haiku Vision pour extraction manuscrite.
- Maquette no-code (PowerApps / Thunkable / FlutterFlow) pour validation par utilisateurs Pro (enseignants pilotes).
- Méthode Agile Scrum, sprints de 2 semaines.
- **Track A** : prototype du module Présence/Notes SMS sur 2 écoles pilotes (modèle LISEC validé 2018).

### Phase 1 — PROTO (Prototype Pro) | Mois 3-6
**Cible : Early adopters PRO (10 enseignants / 3 écoles pilotes à Moroni et Mutsamudu)**

- Application Android native fonctionnelle (Flutter).
- **Track A complet** : module Présence/Absence (parents seulement) + Notes temps réel (parents + élèves) opérationnel.
- **Track B v1** : Modules Scan, OCR, Diagnostic basique, 50 micro-exercices générés.
- Validation hypothèses Lean Startup avec enseignants.
- Itération produit pour Product-Market Fit pédagogique.

### Phase 2 — MVP Public (test grand public) | Mois 6-9
**Cible : Public pilote + investisseurs**

- 200-500 élèves comoriens en pilote (gratuit Track A, freemium Track B).
- **Track A** : déploiement sur les 10 écoles pilotes (~3000-5000 élèves potentiels couverts).
- **Track B** : Fonctionnalités complètes — Scan, IA Vision, 500+ exercices, Profil parent, Notifications.
- Modèle freemium en place.
- Lancement payant fin de phase (semaine / mois / trimestre).

### Phase 3 — Lancement Commercial Y1 | Mois 9-15
**OKR Y1 : 25 % de pénétration des écoles pilotes**

| Trimestre | Cible pénétration | Cible utilisateurs Comores |
|-----------|-------------------|----------------------------|
| Q1 | 5 % | ~8 000 élèves |
| Q2 | 10 % | ~16 000 élèves |
| Q3 | 15 % | ~24 000 élèves |
| Q4 | 25 % | ~40 000 élèves |

**Début Y2 : 50 % de pénétration → ~80 000 élèves comoriens, élargissement Kenya/Tanzanie pour atteindre les 200 000.**

Features prioritaires :
- Présence/absence (ciblage parents) — Track A
- Note temps réel (ciblage parents + élèves) — Track A
- Scan + Diagnostic IA (Track B) — devient le différenciateur premium

Encaissement physique via écoles (ticket recharge LISEC-like) + Mobile Money Hollo/Mvola.

### Phase 4 — Scale Y2 | Mois 15-30
- Expansion Kenya, Tanzanie, Madagascar.
- 250 000 utilisateurs cible.
- Audio-first (IA vocale en swahili / français / comorien shikomori).
- B2B écoles privées : 100 contrats licence annuelle.

### Phase 5 — Leadership Y3 | Mois 30-42
- Expansion RDC, Rwanda, Ouganda.
- 1 M utilisateurs cible.
- 10 M $ ARR.
- Levée Série A pour expansion Afrique de l'Ouest (Sénégal, Côte d'Ivoire, Cameroun, Nigeria).

---

## 10. PROJECTIONS FINANCIÈRES Y1-Y3

### Synthèse

| KPI | Y1 | Y2 | Y3 |
|-----|----|----|----|
| Utilisateurs actifs | 50 000 | 250 000 | 1 000 000 |
| Conversion premium | 10 % | 12 % | 15 % |
| ARPU annuel premium | ~100 $ | ~85 $ | ~67 $ |
| **ARR** | **500 000 $** | **2 500 000 $** | **10 000 000 $** |
| Jalon | Product-Market Fit | Expansion géographique | Leadership Afrique |

### Hypothèses Clés
- **Break-even : Mois 18** post-lancement commercial.
- ARPU décroît avec l'échelle (acquisition de tiers plus modestes) compensé par le volume.
- Coût IA (Vision API + LLM) : ~0,02 $ par scan, amorti à 5+ scans/mois/user payant.
- Coût acquisition CAC : 2,50 $ Y1 → 1,80 $ Y3 (effets de réseau + télcos sponsoring).

### Besoins en Financement Estimés
- **Seed (Mois 0-12) :** 500 K $ — équipe core 8 personnes, infrastructure, marketing pilote.
- **Pré-Série A (Mois 12-24) :** 2 M $ — expansion Kenya/Tanzanie, équipe 20+.
- **Série A (Mois 24-36) :** 8-10 M $ — scale Afrique francophone et anglophone.

---

## 11. ÉQUIPE & ORGANISATION

### Structure Cible Y1 (8 personnes)

| Rôle | Localisation | Mission |
|------|-------------|---------|
| CEO / Founder | Moroni / Nairobi | Vision, fundraising, partenariats stratégiques |
| CTO / Head of Engineering | Nairobi | Architecture, recrutement tech |
| ML / AI Engineer | Nairobi ou remote | OCR, BKT, pipeline IA |
| Mobile Lead (Flutter) | Nairobi ou Kinshasa | App Android |
| Backend Lead (Python/FastAPI) | Remote | API, infra |
| Pedagogical Lead | Moroni / Kenya | Knowledge Graph, curriculums, validation contenus |
| Growth / Marketing Lead | Nairobi | Funnel acquisition, partenariats écoles |
| Customer Success / Support | Moroni / Nairobi | Modération, support multilingue |

### Conseil Pédagogique
Validation continue des contenus par des inspecteurs académiques nationaux (Kenya, Tanzanie, Comores).

---

## 12. RISQUES & MITIGATION

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|-----------|
| Qualité OCR insuffisante sur écriture enfant | Moyenne | Élevé | Fine-tuning modèle sur corpus local 10K copies ; fallback Claude/GPT Vision pour cas difficiles |
| Faible pouvoir d'achat / churn élevé | Élevée | Élevé | Tier hebdomadaire à 1,50 $ ; sponsoring telcos zero-rating |
| Concurrence Google/Khan investit Afrique | Faible | Critique | Moat curriculum local + données comportementales propriétaires |
| Latence réseau 2G/3G | Élevée | Moyen | Offline-first SQLite + compression Opus + CDN local Nairobi/Lagos/Kinshasa |
| Données mineures / conformité | Moyenne | Critique | Chiffrement AES-256 + serveurs locaux + consentement parental explicite + DPO interne |
| Refus écoles / instituts académiques | Moyenne | Moyen | Conseil pédagogique d'inspecteurs académiques ; co-branding écoles |
| Risque change KMF/USD | Élevée | Moyen | Encaissement multi-devise + compte offshore (Maurice/Seychelles) pour réserves |

---

# PARTIE II — CAHIER DES CHARGES FONCTIONNEL

## 13. PERSONAS & CAS D'USAGE

### Persona 1 — Amina, 11 ans, élève CM2 (Moroni)
- A un cahier de devoirs corrigé chaque soir.
- Partage le smartphone Android entry-level de sa mère.
- Connexion 3G intermittente.
- **Besoin :** comprendre pourquoi elle a faux à un exercice, sans attendre l'aide d'un adulte.
- **Frustration actuelle :** le prof a corrigé mais ne réexplique pas individuellement.

### Persona 2 — Fatima, 38 ans, maman d'Amina, infirmière
- Trois enfants scolarisés.
- Suit la scolarité mais ne sait pas aider en mathématiques.
- Paie en Mobile Money (Hollo + Mvola).
- **Besoin :** savoir où ses enfants ont des difficultés, et que ce soit corrigé.
- **Frustration actuelle :** elle découvre les lacunes au moment des examens trimestriels.

### Persona 3 — Mohamed, 14 ans, élève 3e (Nairobi)
- Smartphone Android personnel d'entrée de gamme.
- Pression d'entrée au lycée (examen national KCPE/KCSE).
- Utilise WhatsApp et TikTok.
- **Besoin :** un coup de pouce ciblé sur ses faiblesses, sans cours rébarbatif.
- **Frustration actuelle :** YouTube est hors curriculum kenyan.

### Persona 4 — Mme Salma, directrice d'école privée (Mutsamudu)
- Dirige une école de 400 élèves.
- Concurrence des écoles voisines.
- **Besoin :** différencier son école par un outil de suivi digital crédible auprès des parents.
- **Frustration actuelle :** les bulletins trimestriels ne suffisent plus comme communication parentale.

### Persona 5 — M. Kassim, enseignant CM1 (Moroni)
- 35 élèves, classe surchargée.
- Corrige 30 cahiers chaque soir.
- **Besoin :** comprendre rapidement quelles notions sont massivement ratées par sa classe.
- **Frustration actuelle :** pas de visibilité agrégée sur les lacunes de la classe.

---

## 14. USER STORIES (par persona)

### Élève (Amina, Mohamed)
- **US01.** En tant qu'élève, je veux scanner ma copie corrigée avec mon smartphone pour comprendre mes erreurs.
- **US02.** En tant qu'élève, je veux que l'IA me dise précisément où j'ai bloqué (pas juste « faux »).
- **US03.** En tant qu'élève, je veux faire 3-4 micro-exercices ciblés sur ma lacune en moins de 10 minutes.
- **US04.** En tant qu'élève, je veux voir mes progrès quotidiens (streak, badges, niveau).
- **US05.** En tant qu'élève, je veux écouter l'explication audio si je ne sais pas bien lire.

### Parent (Fatima)
- **US06.** En tant que parent, je veux créer un profil pour chacun de mes enfants.
- **US07.** En tant que parent, je veux recevoir un rapport hebdomadaire par SMS sur les progrès de mon enfant.
- **US08.** En tant que parent, je veux voir un tableau clair des forces et faiblesses (par matière, par concept).
- **US09.** En tant que parent, je veux payer en Mobile Money sans carte bancaire.
- **US10.** En tant que parent, je veux activer le renouvellement automatique de l'abonnement.

### Enseignant / École (M. Kassim, Mme Salma)
- **US11.** En tant qu'enseignant, je veux voir les lacunes agrégées de ma classe pour adapter mon cours.
- **US12.** En tant que directeur d'école, je veux acheter en gros des licences pour mon école.
- **US13.** En tant que directeur, je veux voir un tableau de bord de progression de l'école.

---

## 15. SPÉCIFICATIONS FONCTIONNELLES DÉTAILLÉES

### Module 1 — Onboarding & Authentification

**F01. Inscription / Création de compte**
- Choix du rôle au démarrage : Élève / Parent / Enseignant / École.
- Champs requis :
  - Numéro de téléphone (utilisé comme identifiant unique).
  - E-mail (optionnel pour Élève, obligatoire pour Parent).
  - Pays + Langue préférée (FR, EN, SW, AR de base).
  - Niveau scolaire (Élève) ou Nombre d'enfants (Parent).
- Génération immédiate d'un soft token côté serveur.

**F02. Authentification OTP (double facteur, type WhatsApp)**
- À la première installation : envoi automatique d'un OTP par SMS au numéro déclaré.
- Validation : l'OTP est lu automatiquement depuis la boîte SMS (Android `SMS Retriever API`) — pas de saisie manuelle.
- Activation simultanée d'un OTP par e-mail pour récupération.
- Reconnaissance d'appareil persistante (Device ID).

**F03. Onboarding 3 écrans**
- Écran 1 : *« Photographie une copie corrigée »* (démo animée).
- Écran 2 : *« L'IA détecte la lacune en 5 secondes »* (démo).
- Écran 3 : *« Fais 3 exercices ciblés et c'est compris »* (CTA *« Scanner ma première copie »*).

---

### Module 2 — Scan & OCR (Cœur Produit)

**F04. Capture caméra optimisée**
- Détection automatique du cadre de la feuille (edge detection).
- Auto-correction perspective (deskew).
- Pré-traitement local : noise removal, binarisation.
- Compression locale avant upload (target : < 200 KB par scan).
- Possibilité de scanner plusieurs pages d'un même devoir.

**F05. Pipeline OCR**
- Envoi de l'image pré-traitée vers le backend.
- OCR primaire via **Google Vision API** (Document Text Detection).
- Fallback / qualité supérieure : **Claude 3 Haiku Vision** ou **GPT-4o-mini Vision** pour les écritures manuscrites difficiles.
- Extraction du texte structuré (énoncés, réponses élève, annotations prof).
- Détection des ratures, annotations rouges, croix.

**F06. Diagnostic IA**
- Mapping texte extrait → concepts du Knowledge Graph (cf. section technique).
- Pour chaque réponse incorrecte :
  - Identification du concept exact bloqué.
  - Classification de l'erreur : erreur de calcul, défaut de logique, oubli de règle, faute conceptuelle.
- Mise à jour du Bayesian Knowledge Tracing du profil.

**F07. Restitution visuelle du diagnostic**
- Affichage de la copie scannée, avec surlignage des erreurs détectées.
- Pop-up explicatif par erreur : *« Tu as oublié la retenue ici »*.
- Étoile verte pour les exercices corrects.

---

### Module 3 — Rattrapage (Remédiation Flash)

**F08. Génération du Pack de Rattrapage**
- 3 à 4 micro-exercices générés instantanément à partir des lacunes identifiées.
- Adaptation au niveau scolaire et au curriculum local.
- Types : QCM, glisser-déposer, calcul à trous, réponse libre courte.
- Génération via LLM (Claude / GPT) avec template + Knowledge Graph en contexte.

**F09. Exécution interactive**
- Interface tactile optimisée mobile.
- Feedback immédiat (correct / incorrect avec explication).
- Sortie audio optionnelle (TTS local ou cloud) — *audio-first* pour zones à faible alphabétisation lecture.
- Animation de récompense (étoile, confettis modestes — pas d'addictivité gamblifiée).

**F10. Algorithme « dé-zoome » (Adaptive Drill-Down)**
- Si l'élève échoue sur un exercice de **Niveau 3** (concept cible) :
  - L'algorithme dé-zoome automatiquement vers un prérequis **Niveau 2**.
  - Si échec Niveau 2 → dé-zoome vers Niveau 1.
- Objectif : réparer la fondation avant de progresser.

**F11. Validation de la séance**
- Une séance est validée si > 75 % des exercices sont réussis.
- Sinon : nouveau pack programmé pour le lendemain.

---

### Module 4 — Profil & Progrès

**F12. Profil de Compétence (Knowledge Graph personnel)**
- Vue arborescente des concepts maîtrisés (vert) / en cours (orange) / non maîtrisés (rouge).
- Filtre par matière (Maths, Français, Anglais, Sciences, etc.).
- Historique chronologique : *« 19 mai 2026 : Lacune détectée sur les multiplications à 2 chiffres »*.

**F13. Streak & Gamification (modérée)**
- Compteur jours consécutifs avec au moins 1 séance complétée.
- Badges concept (« Maître des fractions »).
- Pas de monnaie virtuelle, pas de loot box, pas de classement public — respect des bonnes pratiques EdTech enfants.

**F14. Rapport Parent**
- Vue agrégée hebdomadaire par enfant.
- Top 3 lacunes traitées + Top 3 concepts maîtrisés.
- Envoi automatique par SMS chaque dimanche soir (option Family).
- Format SMS court : *« Amina cette semaine : 4 séances ✅, lacune comblée : fractions équivalentes, lacune en cours : règle de trois. »*

---

### Module 5 — Paiement & Abonnement

**F15. Choix du plan**
- 3 plans présentés : Lite (Gratuit) / Pro (1,50 $/sem) / Family (4 $/mois).
- Comparatif clair en tableau (3 colonnes).

**F16. Paiement Mobile Money**
- Intégration : M-Pesa (Safaricom), Orange Money, Airtel Money, Mvola, Hollo, Huri Money.
- Workflow STK Push (pull payment) : saisie numéro → notification au téléphone → confirmation PIN.
- Confirmation immédiate dans l'app.

**F17. Compte de Services / Crédit prépayé**
- Solde en USD ou monnaie locale.
- Achat de packs : 7 jours / 30 jours / 90 jours.
- Renouvellement automatique opt-in (compte rechargé tant qu'il y a du solde).
- Notification 24h avant expiration.

**F18. Ticket de recharge (school reseller)**
- Codes 12 caractères vendus en physique par les écoles ou kiosques.
- Saisie dans l'app pour créditer le compte.

---

### Module 6 — Espace Parent multi-enfants

**F19. Gestion multi-profils**
- Jusqu'à 4 profils enfants dans un compte Family.
- Switch rapide entre profils (style Netflix).
- PIN parent pour accès aux paramètres / paiement.

**F20. Dashboard Parent**
- Carte par enfant (niveau, dernière activité, ratio maîtrise).
- Alertes intelligentes : *« Amina n'a pas scanné depuis 3 jours »*.

---

### Module 7 — Espace École (B2B)

**F21. Dashboard École (web responsive)**
- Vue agrégée classe par classe.
- Heatmap des lacunes massives (« 60 % des CM2 bloquent sur la division »).
- Export CSV des progressions.

**F22. Gestion licences**
- Achat groupé de licences (par lot de 50 / 100 / 500 élèves).
- Génération et impression de tickets d'activation pour distribution aux familles.

---

### Module 8 — IA Conversationnelle (Tuteur Vocal)

**F23. Tuteur audio (option Pro)**
- À la demande de l'élève, l'IA explique vocalement un exercice.
- Voix synthétique multilingue (FR, EN, SW, plus tard shikomori).
- Compression Opus pour usage 2G/3G fluide.

**F24. Chat texte avec le Tuteur**
- Posez une question libre : *« Comment on fait pour les fractions ? »*.
- Réponse contextualisée au Knowledge Graph de l'élève + curriculum local.
- Garde-fous : pas de réponses hors-sujet, pas de contenu inadapté.

---

### Module 9 — Présence / Assiduité (Track A — héritage LISEC)

**F25. Pointage présence enseignant (côté école)**
- L'enseignant pointe les élèves présents / absents en classe via interface tablette ou téléphone (1 clic par élève).
- Génération automatique d'un appel et envoi des alertes parents en temps quasi-réel (< 5 minutes).
- Mode offline avec sync différé (zones réseau faible).

**F26. Notification parent — absence**
- À la première heure d'absence détectée : **SMS automatique au parent** : *« Bonjour, votre enfant Amina n'est pas présente ce matin au CM2 B. Si c'est une erreur, contactez l'école au [tel]. »*
- Push notification dans l'app si l'utilisateur l'a installée.
- Coût SMS internalisé dans l'abonnement (~1 KMF/SMS via accord opérateur).

**F27. Rapport hebdomadaire d'assiduité**
- Récapitulatif des absences / retards de la semaine envoyé chaque dimanche.
- Visualisation graphique dans l'app (calendrier coloré).

**F28. Justification numérique des absences**
- Le parent peut directement justifier une absence depuis l'app (motif + justificatif photo si nécessaire).
- L'enseignant valide / refuse.

---

### Module 10 — Notes en Temps Réel (Track A — héritage LISEC)

**F29. Saisie de notes par l'enseignant**
- Interface enseignant : saisie rapide des notes des évaluations (devoirs, interrogations, examens).
- Choix matière + type d'évaluation + barème.
- Bulk import (CSV ou scan d'une feuille de notes manuscrite via OCR).

**F30. Notification parent et élève — note publiée**
- À la publication d'une note par l'enseignant :
  - **Parent (option Pro/Family)** : SMS + push.
  - **Élève (option Pro)** : push uniquement.
- Délai garanti : < 10 minutes après saisie enseignant.

**F31. Bulletin numérique**
- Vue agrégée par matière, par trimestre.
- Moyennes calculées automatiquement, comparaison avec la moyenne de classe (anonymisée).
- Historique pluriannuel (livret scolaire numérique permanent).

**F32. Alertes intelligentes**
- *« La moyenne d'Amina en maths a baissé de 3 points ce trimestre — voulez-vous activer les exercices ciblés Nasoma ? »* (cross-sell intelligent vers Track B).

---

### Module 11 — Modes de paiement multiples (Comores prioritaire)

**F33. Tickets de recharge physiques (LISEC-style)**
- Distribution via les écoles : codes 12 caractères vendus 100 KMF / 300 KMF / 1000 KMF.
- L'école achète en gros (prix dégressif), revend au détail avec commission 10-15 %.
- Saisie en 1 clic dans l'app pour activer un abonnement Track A ou Track B.

**F34. Paiement Mobile Money intégré**
- Hollo (Comores Telecom), Mvola (Telma) prioritaires pour le marché Comores.
- M-Pesa, Orange Money, Airtel Money pour les marchés Y2.
- Workflow STK Push (déjà détaillé F16).

**F35. Compte famille pré-payé**
- Solde commun famille rechargeable par tous les moyens ci-dessus.
- Allocation auto à chaque enfant selon les services activés.
- Suivi mensuel des dépenses dans l'app.

---

## 16. PARCOURS UTILISATEUR (USER FLOWS)

### Flow A — Premier Scan (Onboarding)

```
[Splash écran « Mimi, Nasoma »]
        ↓
[Choix rôle : Élève / Parent / Enseignant / École]
        ↓
[Saisie téléphone + pays + langue]
        ↓
[Auto-récupération OTP par SMS (SMS Retriever API)]
        ↓
[3 écrans d'onboarding animés]
        ↓
[CTA principal : "Scanner ma première copie"]
        ↓
[Permission caméra]
        ↓
[Capture guidée (cadre vert, détection automatique)]
        ↓
[Validation utilisateur de la photo]
        ↓
[Animation "L'IA analyse…" (3-5 sec)]
        ↓
[Restitution : copie surlignée + diagnostic]
        ↓
[CTA "Lancer le rattrapage flash"]
        ↓
[Pack de 3-4 exercices interactifs]
        ↓
[Écran de fin : "Bravo ! Lacune comblée. À demain ?"]
        ↓
[Prompt d'activation des notifications]
```

### Flow B — Conversion Premium

```
[Élève finit séance gratuite jour 1]
        ↓
[Jour 2 : nouveau scan → propose pack mais demande upgrade après 3 exercices]
        ↓
[Écran d'abonnement : Pro 1,50 $/sem (mis en avant) vs Family 4 $/mois]
        ↓
[Sélection Pro]
        ↓
[Saisie numéro Mobile Money]
        ↓
[STK Push → notification téléphone]
        ↓
[Saisie PIN MM sur l'écran natif du téléphone]
        ↓
[Confirmation backend → activation Pro instantanée]
        ↓
[Retour à la séance, exercice 4 débloqué]
```

### Flow C — Rapport Parent SMS hebdomadaire

```
[Cron job dimanche 19h locale]
        ↓
[Backend agrège data des 7 derniers jours par enfant]
        ↓
[Template SMS rempli : "Amina cette semaine : ..."]
        ↓
[Envoi via gateway SMS (Twilio / Africa's Talking)]
        ↓
[Logging dans backend pour analytics]
```

---

## 17. WIREFRAMES & ÉCRANS (SPÉCIFICATIONS)

> Cette section décrit chaque écran de manière précise pour que l'IA codeuse génère les composants Flutter correspondants.

### Écran 1 — Splash
- Logo Nasoma centré, animation lottie 1,5 s.
- Fond noir #000000.
- Texte « Mimi, Nasoma. » en bas, couleur Vert lime #D4FF80.

### Écran 2 — Choix du rôle
- AppBar transparente avec back arrow.
- Titre H1 : « Tu es… »
- 4 grandes cartes verticales (icône + label) : Élève / Parent / Enseignant / École.

### Écran 3 — Login OTP
- Champ téléphone international (drapeau + indicatif).
- CTA « Recevoir le code ».
- Écran intermédiaire OTP : 6 cases auto-fill via SMS Retriever.

### Écran 4 — Home Dashboard Élève
- Card hero : « Scanner ma copie du jour » (gros bouton vert).
- En-dessous : streak (« Tu as 5 jours consécutifs 🔥 »).
- Liste horizontale : 3 dernières séances avec score.
- Navigation bottom : Home / Progrès / Profil.

### Écran 5 — Scan Caméra
- Plein écran caméra.
- Overlay cadre vert dynamique (détection bordure).
- Bouton capture central + bouton flash + bouton galerie.
- Texte d'aide en bas : « Aligne ta copie dans le cadre ».

### Écran 6 — Diagnostic
- Photo de la copie en haut (50 % de l'écran).
- Surlignages rouge sur les erreurs, vert sur les bonnes réponses.
- Tap sur une zone → bottom sheet explicative.
- CTA bas : « Lancer le rattrapage (3 exercices) ».

### Écran 7 — Exercice
- En-tête : numéro exo (1/4), barre de progression.
- Énoncé clair (police lisible 18sp+).
- Zone réponse adaptée au type (QCM, input, drag&drop).
- Bouton « Écouter l'énoncé » (lecture TTS audio).
- Bouton « Valider ».

### Écran 8 — Profil & Progrès
- Vue arborescente par matière.
- Cercles colorés par concept (rouge/orange/vert).
- Filtre par matière en haut.

### Écran 9 — Espace Parent (multi-profils)
- Carte par enfant en haut.
- Tap sur enfant → vue détaillée individuelle.
- CTA « Ajouter un enfant ».

### Écran 10 — Paramètres / Abonnement
- État actuel de l'abonnement.
- Bouton « Améliorer mon plan ».
- Liste : Notifications / Langue / Confidentialité / Aide / Déconnexion.

---

## 18. RÈGLES MÉTIER

- **R01.** Un scan = un événement diagnostiqué. Pas de scan multiple groupé dans le MVP.
- **R02.** Le profil de compétence est mis à jour SEULEMENT après validation utilisateur du diagnostic.
- **R03.** Un concept est considéré « maîtrisé » si l'élève a réussi 3 exercices consécutifs dessus sur 3 sessions différentes (anti-luck).
- **R04.** Un concept est considéré « bloqué » si l'élève échoue 2 fois dessus en 7 jours.
- **R05.** Le rapport SMS parent est envoyé uniquement sur l'abonnement Family, le dimanche 19h heure locale.
- **R06.** Un compte Lite gratuit a un quota de **5 scans par jour** (anti-abus).
- **R07.** Un compte Pro a un quota de **30 scans par jour**.
- **R08.** Le crédit Mobile Money expire 90 jours après dernier achat.
- **R09.** Les données d'un enfant < 13 ans nécessitent consentement explicite parent (case à cocher RGPD-like).
- **R10.** Tous les contenus pédagogiques générés par LLM sont passés par un filtre de modération (safety + curriculum compliance).

---

## 19. CRITÈRES D'ACCEPTATION MVP

### MVP est considéré comme livré quand :

✅ Application Android installable depuis APK direct ET depuis Google Play Store en pilote interne (closed testing).
✅ Flow complet Scan → Diagnostic → Rattrapage fonctionnel end-to-end.
✅ OCR fonctionnel sur 80 %+ des copies test (corpus 200 copies réelles).
✅ Knowledge Graph de 500 concepts initiaux (Maths CM1-CM2 + Français CM1-CM2 pour le pilote Comores).
✅ 100 micro-exercices générés et validés pédagogiquement.
✅ Authentification OTP fonctionnelle.
✅ 1 méthode de paiement Mobile Money intégrée (idéalement Hollo pour Comores).
✅ Dashboard parent basique fonctionnel.
✅ Mode offline minimum : consultation du profil et exercices déjà téléchargés.
✅ Crashs < 1 % des sessions.
✅ Performance : Scan → Diagnostic en < 8 secondes sur Android entry-level.

---

# PARTIE III — CAHIER DES CHARGES TECHNIQUE

> **Important pour l'IA codeuse :** Cette section contient toutes les spécifications nécessaires à la génération automatique du code. Suivez-la dans l'ordre. Chaque sous-section précise le **stack**, le **schéma**, les **endpoints**, les **modèles de prompts IA**, et les **étapes de build**.

---

## 20. ARCHITECTURE GÉNÉRALE

### Vue d'ensemble — Architecture Edge-Cloud Hybride

```
┌─────────────────────────────────────────────────────────┐
│                  CLIENT MOBILE (Flutter)                │
│  - UI Flutter / Dart                                    │
│  - SQLite local (offline-first)                         │
│  - Camera preprocessing (cropping, deskew)              │
│  - Cache exercices + profil                             │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS + JWT
                         ↓
┌─────────────────────────────────────────────────────────┐
│              API GATEWAY (FastAPI/Python)               │
│  - Auth (JWT + OTP)                                     │
│  - Rate limiting                                        │
│  - Routing microservices                                │
└──┬──────────────┬───────────────┬───────────────┬───────┘
   ↓              ↓               ↓               ↓
┌──────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│Auth  │    │  OCR     │    │  BKT     │    │  Payment │
│Svc   │    │  Vision  │    │  Engine  │    │  Svc     │
└──┬───┘    │  Svc     │    └────┬─────┘    └────┬─────┘
   │        └────┬─────┘         │               │
   │             ↓               ↓               ↓
   │     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │     │ Google Vision│  │PostgreSQL+   │  │Mobile Money  │
   │     │  + Claude/   │  │Knowledge     │  │APIs (Hollo,  │
   │     │  GPT Vision  │  │Graph (Neo4j) │  │M-Pesa,Orange)│
   │     └──────────────┘  └──────────────┘  └──────────────┘
   ↓
┌──────────────┐
│ PostgreSQL   │     ┌─────────────┐
│ users / auth │     │  Redis      │ (cache, sessions)
└──────────────┘     └─────────────┘
                     ┌─────────────┐
                     │  S3 / R2    │ (stockage images scannées)
                     └─────────────┘
                     ┌─────────────┐
                     │  SMS Gateway│ (Twilio / Africa's Talking)
                     └─────────────┘
```

### Patterns Architecturaux
- **Offline-First** : Toutes les fonctionnalités cœur (consultation profil, exercices téléchargés) marchent sans réseau. Sync en arrière-plan.
- **Edge Preprocessing** : Le pré-traitement de l'image (cropping, deskew, compression) se fait sur le device pour réduire la bande passante.
- **Microservices** : services indépendants (Auth, OCR, BKT, Payment) déployés sur AWS Lambda (auto-scaling pics examens).
- **Event-Driven** : événements clés (scan, séance complétée) émis sur file (SQS/RabbitMQ) pour analytics & rapports SMS.

### Multi-tenant
- Tenant = pays (Comores, Kenya, Tanzanie, RDC...).
- Chaque tenant a son Knowledge Graph (curriculum local) et sa configuration (langue, devise, gateway MoMo).

---

## 21. STACK TECHNOLOGIQUE

### Frontend Mobile (App Android, plus tard iOS)
| Couche | Technologie | Version cible |
|--------|-------------|---------------|
| Framework | **Flutter** | 3.22+ |
| Langage | Dart | 3.4+ |
| State management | **Riverpod** | 2.5+ |
| Navigation | go_router | 14+ |
| Base locale | **sqflite** (SQLite) | 2.3+ |
| HTTP client | **dio** | 5.4+ |
| Caméra | camera, image_cropper | latest |
| Image preprocessing | image, opencv_dart (optionnel) | latest |
| Authentification | local OTP read via **sms_autofill** | latest |
| TTS audio | flutter_tts | latest |
| Audio player | just_audio | latest |
| Notifications | flutter_local_notifications + Firebase Cloud Messaging | latest |
| Mobile Money SDK | Custom (REST direct vers backend) | — |
| Analytics | Firebase Analytics + Mixpanel | latest |

### Backend
| Composant | Technologie | Notes |
|-----------|-------------|-------|
| API Framework | **FastAPI (Python 3.12)** | Async, OpenAPI auto |
| ORM | SQLAlchemy 2.0 + Alembic migrations | |
| Database principale | **PostgreSQL 16** | Sur RDS AWS |
| Knowledge Graph | **Neo4j** ou Postgres + recursive CTEs | Choix selon complexité |
| Cache | **Redis 7** | sessions, rate limiting |
| Storage objets | **S3 / Cloudflare R2** | images scannées (90j retention) |
| Queue | **AWS SQS** ou Celery + Redis | |
| Auth | JWT (PyJWT) + OTP via SMS | |
| Logs | structlog + CloudWatch | |

### IA / ML
| Service | Usage |
|---------|-------|
| **Google Cloud Vision API** | OCR primaire, Document Text Detection |
| **Anthropic Claude 3 Haiku (Vision)** | OCR fallback + extraction structurée des erreurs |
| **OpenAI GPT-4o-mini** ou **Claude Haiku** | Génération d'exercices, explications |
| **TTS** : Google Cloud TTS ou Azure Speech | Voix multilingue (FR/EN/SW) |
| **OpenCV** (server-side) | Pré-traitement avancé si nécessaire |
| Modèle BKT custom | Python, scikit-learn ou pgmpy |

### Infrastructure & DevOps
| Composant | Choix |
|-----------|-------|
| Cloud | **AWS** (région af-south-1 Cape Town + eu-west-3 Paris fallback) |
| Conteneurisation | Docker + Docker Compose (dev) |
| Orchestration | AWS ECS Fargate (services) + Lambda (jobs courts) |
| CDN | **Cloudflare** (cache statique + Workers edge en Afrique) |
| CI/CD | GitHub Actions |
| IaC | Terraform |
| Monitoring | CloudWatch + Sentry (errors) + Grafana |
| SMS Gateway | **Africa's Talking** (Afrique Est/Centrale) + Twilio (fallback) |

### Paiements
- **Stripe Connect** (cartes diaspora)
- **Flutterwave** ou **Paystack** (multi-pays, cartes + Mobile Money agrégé)
- Intégrations directes : Hollo (Comores), Mvola (Comores), M-Pesa (Kenya), Airtel Money, Orange Money

---

## 22. MODÈLE DE DONNÉES (SCHÉMAS BDD)

### Tables principales PostgreSQL

```sql
-- ============================================================
-- TENANTS / PAYS
-- ============================================================
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(8) UNIQUE NOT NULL, -- 'KM', 'KE', 'TZ', 'CD'
    name VARCHAR(80) NOT NULL,
    default_locale VARCHAR(10) NOT NULL, -- 'fr-KM', 'sw-KE', 'en-KE'
    currency VARCHAR(3) NOT NULL, -- 'KMF', 'KES', 'TZS', 'CDF'
    momo_providers JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- USERS (élèves, parents, enseignants)
-- ============================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(120),
    role VARCHAR(16) NOT NULL CHECK (role IN ('student','parent','teacher','school_admin')),
    locale VARCHAR(10) DEFAULT 'fr-KM',
    full_name VARCHAR(120),
    grade_level VARCHAR(8), -- 'CM1', 'CM2', '6e', etc.
    encrypted_pii BYTEA, -- chiffrement AES-256 pour données sensibles
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ
);

CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_tenant ON users(tenant_id);

-- ============================================================
-- LIENS PARENT-ENFANT
-- ============================================================
CREATE TABLE family_links (
    parent_id UUID REFERENCES users(id),
    child_id UUID REFERENCES users(id),
    relationship VARCHAR(20) DEFAULT 'parent',
    consent_given_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (parent_id, child_id)
);

-- ============================================================
-- OTP CHALLENGES
-- ============================================================
CREATE TABLE otp_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    code_hash VARCHAR(128) NOT NULL,
    channel VARCHAR(8) NOT NULL, -- 'sms', 'email'
    expires_at TIMESTAMPTZ NOT NULL,
    consumed_at TIMESTAMPTZ,
    attempts SMALLINT DEFAULT 0
);

-- ============================================================
-- KNOWLEDGE GRAPH — CONCEPTS
-- ============================================================
CREATE TABLE subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    code VARCHAR(20) UNIQUE NOT NULL, -- 'MATH', 'FR', 'SVT'
    name VARCHAR(60) NOT NULL
);

CREATE TABLE concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID REFERENCES subjects(id),
    code VARCHAR(40) UNIQUE NOT NULL, -- 'MATH_CM2_FRAC_EQUIV'
    name VARCHAR(200) NOT NULL,
    grade_level VARCHAR(8) NOT NULL,
    difficulty SMALLINT NOT NULL, -- 1 (facile) à 5 (complexe)
    curriculum_refs JSONB, -- {"CBC": "M.5.1.2", "NECTA": "..."}
    description TEXT
);

CREATE TABLE concept_prerequisites (
    concept_id UUID REFERENCES concepts(id),
    prereq_id UUID REFERENCES concepts(id),
    weight FLOAT DEFAULT 1.0,
    PRIMARY KEY (concept_id, prereq_id)
);
-- Cette table modélise le DAG des compétences :
-- "FRACTIONS_EQUIVALENTES" requires "MULTIPLICATION_2DIGITS" + "DIVISION_BASIC"

-- ============================================================
-- BKT — PROFIL DE COMPÉTENCE BAYÉSIEN
-- ============================================================
CREATE TABLE student_concept_mastery (
    student_id UUID REFERENCES users(id),
    concept_id UUID REFERENCES concepts(id),
    mastery_probability FLOAT DEFAULT 0.1, -- p(L) initial
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    attempts INTEGER DEFAULT 0,
    successes INTEGER DEFAULT 0,
    PRIMARY KEY (student_id, concept_id)
);
-- Paramètres BKT (peuvent être par concept) :
-- p_init = 0.1, p_transit = 0.2, p_slip = 0.1, p_guess = 0.25

-- ============================================================
-- SCANS (devoirs photographiés)
-- ============================================================
CREATE TABLE scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES users(id),
    image_s3_key VARCHAR(256) NOT NULL,
    thumbnail_s3_key VARCHAR(256),
    subject_id UUID REFERENCES subjects(id),
    status VARCHAR(16) DEFAULT 'pending', -- pending|processing|done|failed
    ocr_raw_text TEXT,
    ocr_provider VARCHAR(16), -- 'gvision', 'claude_haiku', 'gpt4o_mini'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE INDEX idx_scans_student_created ON scans(student_id, created_at DESC);

-- ============================================================
-- DIAGNOSTICS (résultats d'analyse IA)
-- ============================================================
CREATE TABLE diagnostics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id UUID REFERENCES scans(id),
    detected_errors JSONB NOT NULL,
    -- Exemple JSONB :
    -- [{"exercise_index": 4, "concept_code": "MATH_CM2_RETENUE",
    --   "error_type": "missing_carry", "evidence_bbox": [x,y,w,h],
    --   "confidence": 0.87}, ...]
    concepts_affected UUID[] NOT NULL,
    summary_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- EXERCICES (templates)
-- ============================================================
CREATE TABLE exercise_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concept_id UUID REFERENCES concepts(id),
    type VARCHAR(20) NOT NULL, -- 'mcq', 'fill_blank', 'drag_drop', 'short_text'
    difficulty SMALLINT NOT NULL,
    template_json JSONB NOT NULL,
    -- {"prompt": "...", "options": ["A","B","C"], "answer": "B", "tts_url": "..."}
    locale VARCHAR(10) NOT NULL,
    validated_by UUID, -- pedagogical reviewer
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- SÉANCES & RÉPONSES
-- ============================================================
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES users(id),
    diagnostic_id UUID REFERENCES diagnostics(id),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    success_rate FLOAT
);

CREATE TABLE session_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id),
    exercise_template_id UUID REFERENCES exercise_templates(id),
    student_answer TEXT,
    is_correct BOOLEAN NOT NULL,
    response_time_ms INTEGER,
    answered_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- ABONNEMENTS & PAIEMENTS
-- ============================================================
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    plan VARCHAR(16) NOT NULL, -- 'lite','pro','family','school'
    status VARCHAR(16) NOT NULL, -- 'active','grace','expired','canceled'
    started_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    auto_renew BOOLEAN DEFAULT TRUE
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    subscription_id UUID REFERENCES subscriptions(id),
    amount_local NUMERIC(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    amount_usd NUMERIC(10,2),
    provider VARCHAR(16) NOT NULL, -- 'mpesa','hollo','mvola','orange','flutterwave'
    provider_ref VARCHAR(120) UNIQUE,
    status VARCHAR(16) NOT NULL, -- 'pending','success','failed','refunded'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- ============================================================
-- RECHARGE TICKETS (codes physiques vendus en école)
-- ============================================================
CREATE TABLE recharge_tickets (
    code VARCHAR(12) PRIMARY KEY,
    plan VARCHAR(16) NOT NULL,
    duration_days SMALLINT NOT NULL,
    school_id UUID,
    sold_at TIMESTAMPTZ,
    redeemed_by UUID REFERENCES users(id),
    redeemed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL
);

-- ============================================================
-- ÉCOLES (B2B)
-- ============================================================
CREATE TABLE schools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(200) NOT NULL,
    admin_user_id UUID REFERENCES users(id),
    licenses_purchased INTEGER DEFAULT 0,
    licenses_used INTEGER DEFAULT 0,
    contact_phone VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID REFERENCES schools(id),
    name VARCHAR(60) NOT NULL,
    grade_level VARCHAR(8) NOT NULL,
    teacher_id UUID REFERENCES users(id)
);

CREATE TABLE class_students (
    class_id UUID REFERENCES classes(id),
    student_id UUID REFERENCES users(id),
    PRIMARY KEY (class_id, student_id)
);

-- ============================================================
-- PRÉSENCE / ASSIDUITÉ (Track A — héritage LISEC)
-- ============================================================
CREATE TABLE attendance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES users(id),
    class_id UUID REFERENCES classes(id),
    teacher_id UUID REFERENCES users(id),
    date DATE NOT NULL,
    period VARCHAR(20) NOT NULL, -- 'morning', 'afternoon' ou créneau précis
    status VARCHAR(16) NOT NULL CHECK (status IN ('present','absent','late','excused')),
    minutes_late INTEGER,
    justification_text TEXT,
    justification_doc_s3_key VARCHAR(256),
    justified_by_parent_id UUID REFERENCES users(id),
    justified_at TIMESTAMPTZ,
    teacher_validation VARCHAR(16) CHECK (teacher_validation IN ('pending','validated','refused')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_attendance_student_date ON attendance_records(student_id, date DESC);
CREATE INDEX idx_attendance_class_date ON attendance_records(class_id, date DESC);

-- ============================================================
-- NOTES SCOLAIRES (Track A — héritage LISEC)
-- ============================================================
CREATE TABLE evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID REFERENCES classes(id),
    teacher_id UUID REFERENCES users(id),
    subject_id UUID REFERENCES subjects(id),
    title VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'devoir', 'controle', 'exam', 'oral'
    max_score NUMERIC(5,2) DEFAULT 20.00,
    coefficient NUMERIC(3,1) DEFAULT 1.0,
    eval_date DATE NOT NULL,
    trimester SMALLINT,
    school_year VARCHAR(10) NOT NULL, -- '2026-2027'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ
);

CREATE TABLE grades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluation_id UUID REFERENCES evaluations(id),
    student_id UUID REFERENCES users(id),
    score NUMERIC(5,2),
    comment TEXT,
    is_absent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (evaluation_id, student_id)
);

CREATE INDEX idx_grades_student ON grades(student_id);

-- ============================================================
-- NOTIFICATIONS PARENT/ÉLÈVE (Push + SMS)
-- ============================================================
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_user_id UUID REFERENCES users(id),
    channel VARCHAR(8) NOT NULL, -- 'push', 'sms', 'email'
    type VARCHAR(40) NOT NULL,   -- 'attendance_absent','grade_published','weekly_report',...
    payload JSONB NOT NULL,
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    provider VARCHAR(20),
    provider_ref VARCHAR(120),
    status VARCHAR(16) DEFAULT 'pending'
);

CREATE INDEX idx_notifications_recipient ON notifications(recipient_user_id, sent_at DESC);

-- ============================================================
-- AUDIT & ANALYTICS
-- ============================================================
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID,
    event_name VARCHAR(40) NOT NULL,
    properties JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_events_created ON events(created_at);
```

### Schéma SQLite local (app)
Réplique allégée pour mode offline :
- `local_user` (id, phone, locale, jwt_cache)
- `local_concepts` (snapshot du knowledge graph téléchargé)
- `local_mastery` (profil compétence, sync delta)
- `local_exercises_cache` (50 dernières exercices joués + 20 à venir)
- `local_scans_pending` (scans à uploader quand connexion revient)
- `local_sessions` (séances accomplies offline, sync delta)

---

## 23. SPÉCIFICATIONS API (REST)

### Convention
- Base URL : `https://api.nasoma.africa/v1`
- Auth : Header `Authorization: Bearer <JWT>`
- Format : JSON
- Erreurs : RFC 7807 (Problem Details)

### Endpoints — Authentification

```
POST /auth/register
Body: { "phone": "+2693xxx", "role": "student", "locale": "fr-KM",
        "tenant_code": "KM", "grade_level": "CM2" }
Response: 201 { "user_id": "...", "otp_sent": true }

POST /auth/verify-otp
Body: { "phone": "+2693xxx", "code": "123456" }
Response: 200 { "access_token": "<JWT>", "refresh_token": "...",
                "user": { "id": "...", "role": "...", ... } }

POST /auth/refresh
POST /auth/logout
GET  /auth/me
```

### Endpoints — Scan & Diagnostic

```
POST /scans
Headers: Authorization: Bearer <JWT>
Body: multipart/form-data
  - image: <jpg/png file, max 2MB>
  - subject_code: "MATH"
  - student_id: <uuid, optional si == self>
Response: 202 Accepted
  { "scan_id": "...", "status": "processing",
    "poll_url": "/scans/{scan_id}", "estimated_ms": 5000 }

GET /scans/{scan_id}
Response: 200
  { "scan_id": "...", "status": "done",
    "diagnostic": {
      "summary": "Lacune détectée : retenue dans la multiplication.",
      "errors": [
        { "exercise_index": 4,
          "concept": {"code":"MATH_CM2_RETENUE","name":"Retenue"},
          "error_type": "missing_carry",
          "evidence_bbox": [120,340,80,50],
          "confidence": 0.91 }
      ],
      "concepts_to_drill": ["MATH_CM2_RETENUE","MATH_CM2_MULTIPLICATION_2D"]
    }
  }

GET /scans?student_id=<uuid>&from=2026-05-01&to=2026-05-31
```

### Endpoints — Sessions de rattrapage

```
POST /sessions
Body: { "diagnostic_id": "...", "max_exercises": 4 }
Response: 200
  { "session_id": "...",
    "exercises": [
       { "id":"...", "type":"mcq", "concept":"...", "prompt":"...",
         "options":[...], "tts_url":"..." },
       ...
    ]
  }

POST /sessions/{session_id}/answers
Body: { "exercise_id": "...", "answer": "B", "response_time_ms": 4500 }
Response: 200 { "correct": true, "explanation": "...",
                "next_exercise_id": "..." }

POST /sessions/{session_id}/complete
Response: 200 { "success_rate": 0.75, "concepts_mastered": [...],
                "next_session_recommended_at": "2026-05-20T18:00:00Z" }
```

### Endpoints — Profil & Progrès

```
GET /students/{student_id}/profile
Response: 200
  { "student": {...},
    "mastery": [
      { "concept_code":"MATH_CM2_FRAC_EQUIV", "name":"Fractions équivalentes",
        "mastery": 0.82, "status": "mastered" },
      ...
    ],
    "stats": { "streak_days": 5, "total_sessions": 23,
               "concepts_mastered": 12, "concepts_in_progress": 4 }
  }

GET /students/{student_id}/timeline
Response: liste chronologique des événements d'apprentissage.
```

### Endpoints — Famille

```
POST /family/add-child
Body: { "child_phone": "+2693yyy", "child_name": "Amina",
        "grade_level": "CM2", "consent": true }
GET /family/dashboard
DELETE /family/children/{child_id}
```

### Endpoints — Paiement

```
GET /plans
Response: liste des plans (avec prix locaux).

POST /payments/momo/initiate
Body: { "plan": "pro", "duration": "weekly",
        "provider": "hollo", "phone": "+2693xxx" }
Response: 202 { "payment_id":"...", "stk_pushed": true,
                "poll_url":"/payments/{payment_id}" }

POST /payments/momo/callback (webhook provider)
Body: signed by provider, verify signature.

GET /payments/{payment_id}

POST /redeem-ticket
Body: { "code": "ABC123XYZ456" }
Response: 200 { "plan":"pro","duration_days":30,"expires_at":"..."}
```

### Endpoints — École (B2B)

```
GET /schools/{school_id}/dashboard
GET /schools/{school_id}/classes/{class_id}/heatmap
POST /schools/{school_id}/licenses/purchase
POST /schools/{school_id}/tickets/generate (génère N codes)
```

### Endpoints — Présence / Assiduité (Track A)

```
POST /attendance/bulk
Body: { "class_id":"...", "date":"2026-05-19", "period":"morning",
        "records":[
          {"student_id":"...","status":"present"},
          {"student_id":"...","status":"absent"},
          {"student_id":"...","status":"late","minutes_late":15}
        ]}
Response: 201 (notifications parents déclenchées async)

GET /students/{student_id}/attendance?from=...&to=...
Response: liste des présences/absences pour la période.

POST /attendance/{record_id}/justify
Body: { "justification_text":"Rendez-vous médical",
        "doc": <multipart fichier optionnel> }
Response: 200 (statut passe à 'pending' validation enseignant)

POST /attendance/{record_id}/validate-justification (enseignant)
Body: { "validation":"validated" | "refused", "note":"..." }

GET /classes/{class_id}/attendance/today (vue enseignant)
```

### Endpoints — Notes scolaires (Track A)

```
POST /evaluations
Body: { "class_id":"...", "subject_id":"...", "title":"DS1 fractions",
        "type":"controle", "max_score":20, "coefficient":2,
        "eval_date":"2026-05-19", "trimester":2 }
Response: 201 { "evaluation_id":"..." }

POST /evaluations/{eval_id}/grades
Body: { "grades":[
          {"student_id":"...","score":15.5},
          {"student_id":"...","score":11.0},
          {"student_id":"...","is_absent":true}
        ]}
Response: 201 (notifications parents/élèves déclenchées async)

POST /evaluations/{eval_id}/grades/bulk-from-scan
Body: multipart : image d'une feuille de notes manuscrite
Response: 200 { "parsed_grades":[...], "review_required": true }
(L'enseignant valide ensuite via POST /grades)

GET /students/{student_id}/grades?subject_id=...&trimester=2&school_year=2026-2027
GET /students/{student_id}/report-card?trimester=2  (bulletin numérique)
GET /classes/{class_id}/grade-stats/{eval_id}  (moyennes classe, anonymisé)
```

### Endpoints — Notifications

```
GET  /notifications?since=...&limit=20
PATCH /notifications/{notif_id}/read
GET  /notifications/preferences
PATCH /notifications/preferences
Body: { "channels":{"sms":true,"push":true,"email":false},
        "categories":{"attendance":true,"grades":true,"weekly_report":true,
                      "marketing":false}}

POST /notifications/parent-weekly-trigger (cron interne)
```

### OpenAPI
- L'API expose `/v1/openapi.json` et `/v1/docs` (Swagger UI).
- Tous les endpoints sont versionnés (`/v1/...`).
- Rate limiting : 60 req/min user, 5 scans/min user free, 30/min user pro.

---

## 24. PIPELINE IA VISION & OCR

### Étapes (côté serveur, asynchrone)

```
[1. Image reçue + stockée S3]
        ↓
[2. Pre-processing avancé (server)]
   - Auto-rotation EXIF
   - Désaturation pour amplifier annotations rouges/vertes
   - Détection des zones d'écriture vs zones imprimées
        ↓
[3. OCR primaire — Google Vision API]
   - Document Text Detection (mieux que Text Detection simple)
   - Extraction bounding boxes + texte
        ↓
[4. Routage qualité]
   - Si confiance > 0.85 : continuer
   - Sinon : appel Claude 3 Haiku Vision en parallèle, on garde le meilleur
        ↓
[5. Extraction sémantique — LLM]
   - Prompt : "Voici le texte OCR d'un devoir d'élève {grade_level} en {subject}.
              Identifie les exercices, les réponses de l'élève, les annotations
              du prof. Retourne JSON {exercises: [{statement, student_answer,
              teacher_marks, is_correct}]}"
   - Modèle : Claude 3 Haiku ou GPT-4o-mini (coût ~0,002 $/scan)
        ↓
[6. Mapping concepts — Knowledge Graph]
   - Pour chaque exercice incorrect, prompt :
     "Concept en jeu dans cet exercice : {statement}, niveau {grade}.
      Choisis parmi cette liste de codes : [MATH_CM2_RETENUE, ...]"
   - Retour : code concept + classification erreur
        ↓
[7. Mise à jour BKT]
   - Pour chaque concept détecté, appliquer la formule bayésienne :
     P(L_n | obs) = P(L_n-1 + transit) * P(obs | L)
        ↓
[8. Génération du résumé humain]
   - Prompt court : "Résume en 1 phrase la lacune principale de cet élève
                     en français simple : {concepts_failed}"
        ↓
[9. Stockage Diagnostic + notification client]
```

### Prompts IA — Exemples Production

**Prompt 1 — Extraction structurée (Vision LLM)**
```text
SYSTEM:
Tu es un assistant pédagogique chargé d'analyser des devoirs d'élèves
africains francophones de niveau {grade_level} en {subject}.
À partir de l'image fournie d'une copie corrigée, identifie pour chaque
exercice numéroté :
1. L'énoncé tel que tu le lis,
2. La réponse de l'élève,
3. Les annotations du professeur (croix, ratures rouges, vert),
4. Si l'exercice est correct (true/false),
5. Si incorrect : la nature précise de l'erreur en moins de 20 mots.

Réponds UNIQUEMENT en JSON valide, sans préambule, suivant ce schéma :
{
  "exercises": [
    { "index": 1, "statement": "...", "student_answer": "...",
      "teacher_marks": "...", "is_correct": false,
      "error_description": "Oubli de retenue en colonne dizaines" }
  ]
}
```

**Prompt 2 — Mapping concept (texte LLM)**
```text
SYSTEM:
Tu disposes d'un référentiel de concepts pédagogiques pour le niveau
{grade_level}, matière {subject}, curriculum {curriculum_code}.
Voici la liste des concepts :
{concept_list_json}

USER:
Pour l'erreur suivante, identifie le code de concept précis et la
catégorie d'erreur.
Erreur : "{error_description}"
Énoncé : "{statement}"

Réponds en JSON :
{ "concept_code": "...", "error_category": "calculation_mistake|
  logic_gap|rule_forgotten|conceptual_misunderstanding",
  "confidence": 0.0-1.0 }
```

**Prompt 3 — Génération de micro-exercices**
```text
SYSTEM:
Tu es un générateur d'exercices pédagogiques alignés sur le curriculum
{curriculum_code}, niveau {grade_level}, matière {subject}.
Tu génères des exercices courts, en français simple, adaptés à un enfant
de {age} ans.
Tu respectes strictement le concept ciblé et ne déborde pas hors curriculum.

USER:
Génère 4 micro-exercices visant le concept "{concept_name}" (code:
{concept_code}). Difficulté progressive : exo 1 niveau 1, exo 2 niveau 1,
exo 3 niveau 2, exo 4 niveau 2.
Types autorisés : mcq, fill_blank, short_text.

Réponds en JSON tableau :
[
  { "type":"mcq", "prompt":"...", "options":["A","B","C","D"],
    "correct":"B", "explanation_short":"...", "tts_text":"..." },
  ...
]
```

### Coûts IA estimés
- OCR Google Vision : ~0,0015 $ / image.
- Vision LLM fallback : ~0,005 $ / image.
- Génération exercices : ~0,003 $ / pack.
- **Total moyen par scan : ~0,012 $.**
- Cible : amorti à partir du 2e scan d'un utilisateur payant.

---

## 25. MOTEUR ADAPTATIF (BAYESIAN KNOWLEDGE TRACING)

### Principe BKT
Modèle probabiliste à 4 paramètres :
- `p_init` : probabilité initiale qu'un élève maîtrise un concept (0,1)
- `p_transit` : probabilité d'apprendre à chaque tentative (0,2)
- `p_slip` : erreur d'inattention sur un concept maîtrisé (0,1)
- `p_guess` : réussite par chance sur concept non maîtrisé (0,25)

### Mise à jour après une observation
```python
def bkt_update(p_known: float, correct: bool,
               p_transit=0.2, p_slip=0.1, p_guess=0.25) -> float:
    """
    Met à jour P(L) après observation.
    """
    if correct:
        numerator = p_known * (1 - p_slip)
        denominator = numerator + (1 - p_known) * p_guess
    else:
        numerator = p_known * p_slip
        denominator = numerator + (1 - p_known) * (1 - p_guess)

    p_known_given_obs = numerator / denominator
    # Apprentissage : transition vers maîtrise
    p_known_next = p_known_given_obs + (1 - p_known_given_obs) * p_transit
    return min(max(p_known_next, 0.0), 1.0)
```

### Seuils
- `p_known >= 0.85` : concept **maîtrisé** (vert)
- `0.50 <= p_known < 0.85` : **en cours** (orange)
- `p_known < 0.50` : **non maîtrisé** (rouge)

### Drill-down adaptatif (algorithme « dé-zoome »)
```
function recommend_exercises(student, target_concept):
    if mastery(student, target_concept) >= 0.85:
        return next_concept_in_graph(target_concept)

    prereqs = get_prerequisites(target_concept)
    weak_prereqs = [p for p in prereqs if mastery(student, p) < 0.50]

    if weak_prereqs:
        # Dé-zoome : revient sur le plus faible prérequis
        return recommend_exercises(student, weak_prereqs[0])
    else:
        return generate_exercises(target_concept, level=current_level)
```

### Knowledge Graph — Format conceptuel
Pour 5000+ concepts, on utilise un DAG (Directed Acyclic Graph).
Implémentation pragmatique : tables `concepts` + `concept_prerequisites` (cf. schéma BDD).
Pour requêtes complexes (chemin optimal, voisins), recursive CTE PostgreSQL ou Neo4j optionnel.

Exemple de graphe (Maths CM2) :
```
MATH_CM2_PROBLEMES_FRACTIONS
   ↑ requires
MATH_CM2_FRAC_EQUIV
   ↑ requires
MATH_CM2_MULTIPLICATION_2D ← requires ← MATH_CM1_TABLES_MULT
   ↑ requires
MATH_CM2_RETENUE
```

---

## 26. SÉCURITÉ & CONFORMITÉ

### Chiffrement
- Tous les transports HTTPS TLS 1.3.
- Données PII chiffrées au repos (champs `encrypted_pii` AES-256-GCM, clé KMS AWS).
- Images scannées : URLs signées S3 (expiration 15 min).
- JWT signés avec clé asymétrique RS256, rotation tous les 90 jours.

### Authentification
- OTP à 6 chiffres, validité 5 minutes, 3 tentatives max.
- JWT access token : 24h. Refresh token : 30 jours, rotation à chaque usage.
- Device binding : token lié au Device ID, révocation possible.

### Protection des mineurs
- Aucune donnée d'un enfant < 13 ans n'est stockée sans **consentement explicite parent** enregistré (case à cocher horodatée).
- Pas de profil public, pas de classement social, pas de chat entre élèves.
- Modération automatique de tout contenu généré par IA (filtre Anthropic/OpenAI safety).
- Pas d'ads ciblées pour mineurs (free tier : ads contextuelles seulement).

### Conformité réglementaire
- **Comores :** Loi 18-008 sur la protection des données personnelles.
- **Kenya :** Data Protection Act 2019 (registration ODPC).
- **Tanzanie :** Personal Data Protection Act 2022.
- **Nigeria :** NDPR 2019 (anticipation expansion).
- **RGPD-like :** approche prudente même hors UE.

### DPO & Politiques
- Désignation d'un DPO (CK Innovation, Moroni).
- Privacy policy + Terms of Service traduits dans toutes les langues cibles.
- Droit à l'effacement implémenté (`DELETE /users/me` → soft delete 30j puis purge totale).
- Droit à la portabilité : export ZIP de toutes les données (`POST /users/me/export`).

### Sécurité applicative
- Validation stricte de toutes les entrées (Pydantic).
- Rate limiting (Redis sliding window).
- Anti-fraud Mobile Money : webhook signature verification + idempotence keys.
- Logs anonymisés (pas de PII dans les logs).
- Pentests semestriels.

---

## 27. DEVOPS & INFRASTRUCTURE

### Environnements
| Env | Usage | Données |
|-----|-------|---------|
| `dev` | Développement local | mock |
| `staging` | QA, démo investisseurs | anonymisées |
| `prod` | Pilote + clients | production |

### Déploiement
- **Backend :** Docker images poussées sur AWS ECR, déployées sur ECS Fargate.
- **Mobile :** Builds via Codemagic ou GitHub Actions, distribués via Firebase App Distribution (test) puis Google Play closed/open testing.
- **IaC :** Terraform pour AWS resources (VPC, RDS, ECS, Lambda, SQS, S3, CloudWatch).

### Monitoring & Observability
- Logs : structlog → CloudWatch.
- Erreurs : Sentry (mobile + backend).
- Metrics : Prometheus + Grafana (latence API, taux OCR, conversions).
- Alertes PagerDuty pour : downtime > 5 min, erreur OCR > 20 %, échec paiement > 10 %.

### CDN & Edge
- Cloudflare devant l'API pour cache statique + Workers Edge en Afrique.
- Serveurs cache locaux : **Nairobi (af-south-1), Lagos (proxy), Kinshasa (PoP)** pour réduire latence < 200 ms sur la zone.

### CI/CD Pipeline (GitHub Actions)
```yaml
on: [push, pull_request]
jobs:
  backend:
    - install python deps
    - lint (ruff)
    - type-check (mypy)
    - unit tests (pytest)
    - integration tests (docker-compose)
    - build docker image
    - push to ECR (sur main)
    - deploy to ECS (sur main)

  mobile:
    - install flutter
    - flutter analyze
    - flutter test
    - flutter build apk --split-per-abi
    - upload to Firebase App Distribution (sur main)
    - tag release + upload Play Store closed track (sur tag)
```

---

## 28. PLAN DE TESTS

### Pyramide de tests

| Niveau | Couverture cible | Outils |
|--------|-----------------|--------|
| Unit (backend) | 80 % | pytest + pytest-asyncio |
| Unit (mobile) | 60 % | flutter_test |
| Integration | scénarios critiques | pytest + testcontainers |
| E2E mobile | 10 scénarios clés | Patrol / Flutter integration_test |
| Manuel UAT | sur 3 pilotes (Comores, Kenya, Tanzanie) | Plan de test rédigé |

### Scénarios E2E à automatiser (mobile)
1. Onboarding complet → premier scan → diagnostic → exercices → fin.
2. Scan offline → upload différé quand réseau revient.
3. Paiement MoMo Hollo (sandbox) → activation Pro.
4. Création profil enfant + consentement parent.
5. Switch entre 2 profils enfants.
6. Réception SMS rapport hebdomadaire (mock gateway).
7. Crash recovery : kill app au milieu d'une séance, reprise.
8. Mode 2G simulé : scan + diagnostic en < 15s.
9. Saisie code ticket recharge → activation.
10. Logout / Login → restauration profil.

### Tests pédagogiques
- **Corpus de validation OCR :** 200 copies réelles (anonymisées) annotées manuellement par des pédagogues, métriques précision/rappel sur les erreurs détectées.
- **Test A/B exercices :** générer 2 variantes d'un exo, soumettre à 50 enfants chacune, mesurer taux de réussite et temps de complétion.

### Performance
- API : P95 < 500 ms (hors OCR).
- OCR end-to-end : P95 < 8 s.
- App cold start : < 3 s sur Android 8+ entry-level.
- Taille APK : < 30 MB (split par ABI).

---

## 29. INSTRUCTIONS DE BUILD STEP-BY-STEP POUR IA CODEUSE

> **Cette section est dédiée à l'agent IA de codage (Claude Code, Kimi K2, emergent.sh, Cursor, Aider...). Suivez chaque étape dans l'ordre.**

### Étape 0 — Pré-requis & comptes à provisionner manuellement

Avant le code, l'humain crée :
1. Compte AWS (région af-south-1 + eu-west-3).
2. Compte Google Cloud (Vision API activée).
3. Compte Anthropic (clé API Claude).
4. Compte OpenAI (clé API).
5. Compte Twilio + Africa's Talking (SMS).
6. Compte développeur Google Play (25 $ one-shot).
7. Domaine `nasoma.africa` ou `nasoma.app`.
8. Sandbox Mobile Money : Hollo (Comores), Safaricom Daraja (M-Pesa).

Les clés API sont stockées dans **AWS Secrets Manager** (jamais dans le code).

---

### Étape 1 — Structure du monorepo

L'IA codeuse crée :
```
nasoma/
├── README.md
├── .env.example
├── docker-compose.yml          # dev local : postgres, redis, localstack S3
├── infra/
│   └── terraform/              # AWS infra
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI entry
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── scans.py
│   │   │   │   ├── sessions.py
│   │   │   │   ├── profile.py
│   │   │   │   ├── family.py
│   │   │   │   ├── payments.py
│   │   │   │   └── schools.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py     # JWT + OTP
│   │   │   ├── db.py
│   │   │   └── logging.py
│   │   ├── models/             # SQLAlchemy ORM
│   │   ├── schemas/            # Pydantic
│   │   ├── services/
│   │   │   ├── ocr_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── bkt_service.py
│   │   │   ├── exercise_generator.py
│   │   │   ├── momo_service.py
│   │   │   └── sms_service.py
│   │   └── workers/            # Celery tasks
│   ├── tests/
│   ├── alembic/                # migrations
│   ├── pyproject.toml
│   └── Dockerfile
├── mobile/                     # Flutter app
│   ├── lib/
│   │   ├── main.dart
│   │   ├── core/
│   │   │   ├── theme/
│   │   │   ├── router/
│   │   │   ├── api/            # dio client + endpoints
│   │   │   └── storage/        # sqflite repos
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   ├── scan/
│   │   │   ├── diagnostic/
│   │   │   ├── session/
│   │   │   ├── profile/
│   │   │   ├── family/
│   │   │   └── payment/
│   │   └── shared/widgets/
│   ├── pubspec.yaml
│   ├── android/
│   └── test/
├── pedagogy/
│   ├── knowledge_graphs/
│   │   ├── KM/                 # Comores
│   │   │   ├── math_cm1.json
│   │   │   ├── math_cm2.json
│   │   │   └── fr_cm2.json
│   │   ├── KE/                 # CBC Kenya
│   │   └── TZ/                 # NECTA Tanzanie
│   └── exercises_seed/         # 100 exos initiaux par pays
└── docs/
    ├── architecture.md
    ├── api.md
    └── runbook.md
```

---

### Étape 2 — Bootstrap backend (FastAPI)

L'IA codeuse exécute (ou simule) :
```bash
cd backend
poetry init --name nasoma-backend --python ^3.12
poetry add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg \
           alembic pydantic[email] python-jose[cryptography] \
           passlib[bcrypt] redis httpx pillow boto3 anthropic openai \
           google-cloud-vision celery[redis] structlog sentry-sdk
poetry add --dev pytest pytest-asyncio ruff mypy testcontainers
```

Puis crée :
- `app/main.py` : instance FastAPI avec CORS, middleware logging, /healthz.
- `app/core/config.py` : Pydantic Settings, lit env vars.
- `app/core/db.py` : engine async + session.
- `app/models/` : un fichier par table du schéma BDD (cf. §22).
- `alembic/versions/0001_init.py` : migration initiale.

---

### Étape 3 — Implémenter les endpoints en priorité MVP

Ordre strict :
1. `auth/register`, `auth/verify-otp` → suffisant pour faire tourner l'app.
2. `scans` POST (upload + queue), GET (poll).
3. Worker Celery `process_scan` qui fait l'orchestration OCR + LLM.
4. `sessions` POST + answers + complete.
5. `students/{id}/profile`.
6. `family/add-child`.
7. `payments/momo/initiate` + webhook callback.
8. `redeem-ticket`.

Pour CHAQUE endpoint :
- Schéma Pydantic input/output.
- Test unitaire happy path.
- Test unitaire erreur (auth, validation).

---

### Étape 4 — Pipeline IA Vision (le cœur)

Créer `app/services/ocr_service.py` :

```python
class OCRService:
    async def process(self, image_bytes: bytes, locale: str, subject_code: str,
                      grade_level: str) -> DiagnosticDTO:
        # 1. Preprocess
        img = self._preprocess(image_bytes)
        # 2. Try Google Vision
        gv_result = await self._google_vision(img)
        confidence = gv_result.confidence
        # 3. If low confidence, use Claude Vision
        if confidence < 0.85:
            cl_result = await self._claude_vision(img, locale, grade_level)
            chosen = cl_result if cl_result.confidence > confidence else gv_result
        else:
            chosen = gv_result
        # 4. LLM extraction structured
        exercises = await self._extract_exercises(chosen.raw_text,
                                                   grade_level, subject_code, locale)
        # 5. Map concepts
        concepts_kg = await self._load_knowledge_graph(locale, subject_code,
                                                       grade_level)
        diagnostic = await self._map_to_concepts(exercises, concepts_kg)
        return diagnostic
```

Implémenter `_claude_vision` avec Anthropic SDK + prompt 1 (cf. §24).
Implémenter `_map_to_concepts` avec prompt 2.

---

### Étape 5 — Moteur BKT

Créer `app/services/bkt_service.py` avec la fonction `bkt_update` (cf. §25).
Créer méthode `recommend_exercises(student_id, target_concept_id)` avec drill-down (cf. §25).
Tests unitaires sur 10 scénarios :
- Élève qui réussit 3 fois de suite → mastery > 0.85.
- Élève qui échoue → recommandation prereq.
- Élève sur concept racine → exercice direct.

---

### Étape 6 — Bootstrap mobile (Flutter)

```bash
cd mobile
flutter create --org africa.nasoma --project-name nasoma .
flutter pub add flutter_riverpod go_router dio sqflite path_provider \
                camera image_picker image_cropper image \
                flutter_secure_storage sms_autofill flutter_tts just_audio \
                firebase_core firebase_messaging firebase_analytics \
                flutter_local_notifications intl
```

Structure features (Riverpod + Repository pattern) :
- `features/auth/` : repository, controller, screens (login, otp).
- `features/scan/` : caméra, preprocessing local, upload, poll.
- `features/diagnostic/` : affichage résultat IA.
- `features/session/` : exercices interactifs.
- `features/profile/` : Knowledge Graph view.
- `features/family/` : multi-profils.
- `features/payment/` : tunnels MoMo.

---

### Étape 7 — Écrans en ordre de priorité (mobile)

1. SplashScreen → Onboarding (3 écrans) → RoleSelector → LoginPhone → OTPScreen → HomeStudent.
2. HomeStudent → ScanScreen (caméra) → ProcessingScreen → DiagnosticScreen.
3. DiagnosticScreen → SessionScreen (exercices) → SessionCompleteScreen.
4. ProfileScreen (Knowledge Graph view).
5. ParentDashboard (multi-profils) + AddChild.
6. SubscriptionScreen + MoMoPaymentScreen + RedeemTicketScreen.
7. SettingsScreen (langue, notifications, déconnexion, suppression compte).

Theming :
- Couleurs : noir #000, vert lime #D4FF80, blanc, gris #1A1A1A.
- Police : Inter (mobile-friendly).
- Dark mode par défaut (économie batterie OLED + esthétique brand).

---

### Étape 8 — Knowledge Graph initial (Comores pilote)

L'IA codeuse génère le fichier `pedagogy/knowledge_graphs/KM/math_cm2.json` avec ~100 concepts cœur, structure :
```json
{
  "subject": "MATH",
  "grade_level": "CM2",
  "concepts": [
    {
      "code": "MATH_CM2_ADD_RETENUE",
      "name": "Addition avec retenue",
      "difficulty": 1,
      "prerequisites": ["MATH_CM1_ADD_SIMPLE"],
      "curriculum_refs": {"COMORES": "M.5.1.2"}
    },
    ...
  ]
}
```
Charger via script Alembic seed.

---

### Étape 9 — Exercices initiaux

Pour chaque concept (initial pack 100), l'IA codeuse génère 5 exercices via le prompt 3 (cf. §24), les passe en revue manuelle, puis bulk-insert dans `exercise_templates`.

---

### Étape 10 — Intégration Mobile Money (Hollo Comores en premier)

Implémenter `MomoService` avec une stratégie par provider :
```python
class MomoProvider(ABC):
    async def initiate_stk_push(self, phone, amount, currency, ref) -> PaymentInit: ...
    async def verify_callback(self, payload, signature) -> PaymentResult: ...

class HolloProvider(MomoProvider): ...
class MpesaProvider(MomoProvider): ...
class OrangeMoneyProvider(MomoProvider): ...
```

Pour le MVP Comores, démarrer avec Hollo. Doc API à demander au provider.

Webhook signed : `POST /v1/payments/momo/callback/{provider}` avec vérification signature.

---

### Étape 11 — Système OTP & SMS

`SmsService` avec abstraction provider (Africa's Talking comme primaire, Twilio fallback).

OTP flow :
- `/auth/register` génère OTP, le hash, le stocke, envoie SMS.
- App utilise `sms_autofill` (Android SMS Retriever API) — SMS doit contenir la signature de l'app.
- `/auth/verify-otp` vérifie hash + expiration + tentatives.

---

### Étape 12 — Mode Offline (Mobile)

Implémenter dans `core/storage/` :
- `OfflineQueue` : table `local_scans_pending` avec champs (id, file_path, payload, retries).
- `SyncService` : exécuté quand connectivity_plus détecte un retour réseau, dépile la queue.
- Cache Knowledge Graph : téléchargé au login, mis à jour delta-by-delta (`GET /kg?since=...`).
- Cache exercices : 20 exercices "à venir" pré-fetchés selon BKT.

---

### Étape 13 — Tests E2E mobile

Implémenter les 10 scénarios E2E (cf. §28) avec `integration_test`.
Pour les scans, utiliser des images fixtures dans `test/fixtures/scans/`.

---

### Étape 14 — Build APK et déploiement Play Store

```bash
cd mobile
flutter build apk --split-per-abi --release
# Signing key géré via Codemagic / GitHub Actions secrets

# Output : build/app/outputs/flutter-apk/app-arm64-v8a-release.apk (~25 MB)
```

Upload sur Google Play Console :
- Track : Internal Testing (pour QA).
- Closed Testing (pour 200-500 pilotes Comores).
- Open Testing → Production (post-MVP validé).

---

### Étape 15 — Lancement du pilote Comores

Une fois MVP en production internal/closed :
1. Identifier 3 écoles primaires privées de Moroni / Mutsamudu.
2. Recruter 200 familles via les écoles (gratuit pendant 3 mois).
3. Distribuer codes ticket recharge gratuits.
4. Onboarding terrain : 1 session par école.
5. Collecter data 30 jours, itérer.
6. Mesurer : nombre de scans / élève / semaine, taux de séances complétées, NPS parent, NPS élève.

---

## ANNEXE A — VARIABLES D'ENVIRONNEMENT

`.env.example` :
```env
# App
APP_ENV=development
APP_BASE_URL=http://localhost:8000
SECRET_KEY=change-me
JWT_PRIVATE_KEY_PATH=/secrets/jwt_private.pem
JWT_PUBLIC_KEY_PATH=/secrets/jwt_public.pem

# Database
POSTGRES_DSN=postgresql+asyncpg://nasoma:nasoma@localhost:5432/nasoma
REDIS_URL=redis://localhost:6379/0

# S3
S3_BUCKET=nasoma-scans-dev
AWS_REGION=af-south-1

# AI Providers
GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp.json
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx

# SMS
AFRICASTALKING_API_KEY=xxxx
AFRICASTALKING_USERNAME=nasoma
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxxx

# Mobile Money
HOLLO_API_KEY=xxxx
HOLLO_API_SECRET=xxxx
MPESA_CONSUMER_KEY=xxxx
MPESA_CONSUMER_SECRET=xxxx

# Sentry / monitoring
SENTRY_DSN=https://xxxx@sentry.io/xxxx
```

---

## ANNEXE B — CHECKLIST AVANT LANCEMENT MVP PILOTE

- [ ] APK signé installable, taille < 30 MB
- [ ] Onboarding < 3 minutes mesuré sur 5 testeurs
- [ ] OCR sur 50 copies test : précision > 80 %
- [ ] 100 micro-exercices validés pédagogiquement
- [ ] Knowledge Graph 500 concepts Maths + Français CM1-CM2 (Comores)
- [ ] Hollo Money sandbox + production OK
- [ ] SMS OTP fonctionnel sur Comores Telecom & Telma
- [ ] Privacy Policy + Terms publiés en français + comorien
- [ ] DPO désigné + procédure exercice des droits documentée
- [ ] Convention pédagogique signée avec 3 écoles pilotes
- [ ] Plan de support utilisateur opérationnel (WhatsApp Business + numéro local)
- [ ] Sentry + Mixpanel intégrés et tableaux de bord opérationnels
- [ ] Plan de rollback en cas de bug critique

---

## ANNEXE C — GLOSSAIRE

- **ARR** : Annual Recurring Revenue
- **ARPU** : Average Revenue Per User
- **BKT** : Bayesian Knowledge Tracing
- **CAC** : Customer Acquisition Cost
- **CBC** : Competency-Based Curriculum (Kenya)
- **LTV** : Lifetime Value
- **MoMo** : Mobile Money
- **NECTA** : National Examinations Council of Tanzania
- **OCR** : Optical Character Recognition
- **OTP** : One-Time Password
- **PMF** : Product-Market Fit
- **STK Push** : SIM Toolkit Push (paiement Mobile Money initié serveur)
- **TAM/SAM/SOM** : Total/Serviceable Available/Obtainable Market

---

## ANNEXE D — RÉFÉRENCES DOCUMENTAIRES INTERNES

Ce document s'appuie sur la documentation interne du projet (10 ans de réflexion CK Innovation sur le sujet) :

**Documentation projet Nasoma (2024-2026)**
- `NASOMA_V0B.md` — Executive Summary stratégique (version actualisée)
- `Nasoma — Dossier Stratégique Consolidé.pdf` (13 slides)
- `Nasoma — Dossier Technique & Business 2026.pdf` (13 slides)
- `Nasoma — L'IA au service de l'éducation.pdf` (13 slides)
- `NDA SOMA / CK Innovation 2024 V1` (cadre juridique de partenariat)

**Documentation projet LISEC / SOMA (2018)**
- `POC_MVP_APPLI_MSOMO-V2-Light.md` — Méthodologie POC/Proto/MVP (Lean/Agile) et stratégie marketing initiale
- `TIC_EDU-LISEC_2018.docx` — Projet de Livret Scolaire Unique Numérique Sécurisé + plan financier détaillé (160 000 élèves, 723 M KMF/an de potentiel)
- `COURRIER-CK-I-COMMISSARIAT-EDU-NG-2018_V1.docx` — Courrier officiel de présentation au Commissaire à l'Éducation de Ngazidja (avril 2018)
- `PA_SIFAM_Consulting_-_KTG_C_(CT1-4)_2018.docx` — Plan d'action stratégique CT 2018-2020 (cadre business plus large)
- `NDA-CK_INNOVATION_COMMISSARIAT-EDU-NGAZIDJA_V1.docx` — Accord de confidentialité signé avec le Commissariat à l'Éducation de Ngazidja
- `NDA-_LISEC_HAMIDOU_KADER_V1.docx` — Accord de confidentialité partenaire technique

**Études de référence sur le système éducatif comorien**
- `Rapport_pasec_Comores_2010.pdf` — Programme d'Analyse des Systèmes Éducatifs de la CONFEMEN, diagnostic complet de l'enseignement primaire comorien (taux d'échec, facteurs de qualité, modélisation économétrique)
- `Statistiques_de_l_éducation.docx` — Statistiques DGPEP / Ministère de l'Éducation comorien (CIPR, établissements publics/privés par île)
- `Réflexion_sur_la_problématique_du_Rendement_scolaire_aux_Comores.docx` — Tribune Dr. Mohamed Ali Mohamed Ph.D. (politique éducative et propositions)
- `CONFERENCENATIONALEDELEDUCATION.pdf` — Acte de la 11ᵉ Conférence Nationale de l'Éducation aux Comores (engagements du Ministre + Commissaires des îles autonomes)
- `11ème_Conférence_nationale_de_l_Education_aux_Comores___discours_de_La_France_en_Union_des_Comores.pdf` — Engagement de la coopération française (PME, AFD, UNICEF, UE)
- `Education___L_éducation_de_base_confiée_aux_communes.pdf` — La Gazette des Comores, transfert de compétences éducatives aux Mairies (août 2017)

**Sources externes principales**
- Banque Mondiale — Learning Poverty 2022 (86 % des enfants africains ne maîtrisent pas la lecture à 10 ans)
- UNESCO Institute for Statistics — Projections démographiques Afrique 2030
- HolonIQ — Africa EdTech Market Report
- CONFEMEN — Données PASEC comparatives 14 pays africains francophones

---

## ANNEXE E — KNOWLEDGE GRAPH INITIAL COMORES (extrait pour seed)

> Cette annexe donne un échantillon concret de Knowledge Graph aligné sur le curriculum comorien APC (Approche Par Compétences) pour la 5ᵉ année primaire (CM2) en mathématiques. L'IA codeuse doit utiliser ce format pour générer 500+ concepts initiaux.

### Exemple — fichier `pedagogy/knowledge_graphs/KM/math_cm2.json` (extrait)

```json
{
  "metadata": {
    "country": "KM",
    "country_name": "Union des Comores",
    "curriculum_code": "APC_KM_2010",
    "curriculum_name": "Approche Par Compétences — Plan Directeur 2010-2015",
    "subject": "MATH",
    "grade_level": "CM2",
    "validated_by": "Pédagogue inspecteur CIPR Ngazidja",
    "version": "1.0"
  },
  "concepts": [
    {
      "code": "MATH_CM2_ADD_RETENUE",
      "name": "Addition avec retenue (3 chiffres)",
      "name_shikomori": "Mfanyihazo wa tahaifu",
      "difficulty": 1,
      "estimated_minutes": 5,
      "prerequisites": ["MATH_CM1_ADD_SIMPLE", "MATH_CM1_VALEUR_POSITION"],
      "curriculum_refs": {"APC_KM": "M.5.1.2", "PASEC": "ARITH_BASIC"},
      "description": "Effectuer une addition de nombres à 3 chiffres avec retenue."
    },
    {
      "code": "MATH_CM2_MULT_2DIGITS",
      "name": "Multiplication à 2 chiffres",
      "difficulty": 2,
      "estimated_minutes": 8,
      "prerequisites": ["MATH_CM1_TABLES_MULT", "MATH_CM2_ADD_RETENUE"],
      "curriculum_refs": {"APC_KM": "M.5.2.1"},
      "common_errors": [
        {"code":"missing_carry","description":"Oubli de la retenue en colonne suivante"},
        {"code":"row_alignment","description":"Décalage de la 2ème ligne incorrect"}
      ]
    },
    {
      "code": "MATH_CM2_FRAC_EQUIV",
      "name": "Fractions équivalentes",
      "difficulty": 3,
      "estimated_minutes": 10,
      "prerequisites": ["MATH_CM2_MULT_2DIGITS","MATH_CM2_DIV_BASIC"],
      "curriculum_refs": {"APC_KM": "M.5.4.2"},
      "common_errors": [
        {"code":"only_numerator","description":"Multiplie seulement le numérateur, pas le dénominateur"},
        {"code":"add_instead_of_mult","description":"Additionne au lieu de multiplier"}
      ]
    },
    {
      "code": "MATH_CM2_PROBLEMES_FRACTIONS",
      "name": "Résolution de problèmes avec fractions",
      "difficulty": 4,
      "estimated_minutes": 15,
      "prerequisites": ["MATH_CM2_FRAC_EQUIV","MATH_CM2_LECTURE_ENONCE"],
      "curriculum_refs": {"APC_KM": "M.5.4.5"}
    }
  ]
}
```

### Matières-niveaux à seeder en priorité (MVP Comores)

| Matière | Niveau | # concepts cible | Priorité |
|---------|--------|------------------|----------|
| Mathématiques | CM1 | 80 | P0 |
| Mathématiques | CM2 | 100 | P0 |
| Français | CM1 | 80 | P0 |
| Français | CM2 | 100 | P0 |
| Mathématiques | 6ᵉ | 100 | P1 |
| Français | 6ᵉ | 80 | P1 |
| Arabe / Coran | CM1-CM2 | 50 | P1 (différenciateur Comores) |
| Sciences | CM2 | 60 | P2 |

**Total seed initial MVP : ~650 concepts.**

### Méthodologie de génération

L'IA codeuse procédera comme suit :
1. **Ingérer** les programmes officiels APC Comores (à scanner / OCRiser via l'app elle-même !).
2. **Générer** une première liste exhaustive de concepts par classe-matière via LLM (prompt template fourni dans le repo).
3. **Annoter** les prérequis (DAG) en croisant avec les programmes des classes inférieures.
4. **Faire valider** par un comité pédagogique de 3 inspecteurs CIPR rémunérés (300-500 € forfait).
5. **Bulk-insert** dans la base via script Alembic `seed_knowledge_graph.py`.

---

## ANNEXE F — ASPECTS JURIDIQUES ET INSTITUTIONNELS COMORES

### Cadre légal applicable
- **Droit applicable** : droit positif de l'Union des Comores.
- **Juridiction** : Cour d'Arbitrage des Comores (CACOM) en cas de différend (procédure médiation puis arbitrage, conformément aux NDA déjà signés).

### Acteurs institutionnels clés
| Institution | Rôle | Action requise |
|-------------|------|----------------|
| **Ministère de l'Éducation Nationale** | Validation curriculum, soutien officiel | Présenter Nasoma à la Conférence Nationale Annuelle de l'Éducation |
| **Commissariat à l'Éducation de Ngazidja** | Tutelle pédagogique île principale | Reprise des relations engagées 2018 (NDA déjà signé) |
| **Commissariats Mwali & Ndzuwani** | Extension à 100 % du territoire | Réplication du modèle Ngazidja |
| **DGPEP** (Direction Générale Planification, Études, Projets) | SISE / Système d'Information Statistique | Possible partenariat data — fourniture anonymisée vs accès cartographie scolaire |
| **CIPR (17)** | Inspecteurs régionaux | Validation pédagogique terrain |
| **Mairies (54, depuis 2017)** | Gestion administrative primaire public | Canal B2G original (sponsoring de comptes Nasoma pour élèves défavorisés) |
| **Université des Comores (UDC)** | Extension marché Y2 + R&D | Partenariat académique pour validation IA |

### Documents juridiques préalables à signer (par CK Innovation / Nasoma)
1. **Mise à jour du NDA** avec Commissariat à l'Éducation de Ngazidja (V2 incluant Nasoma).
2. **Convention de partenariat pilote** avec 3 écoles privées (Maison des Enfants, et 2 autres).
3. **Convention de partenariat institutionnel** Ministère + DGPEP (cadre data + curriculum).
4. **CGU Nasoma** (Conditions Générales d'Utilisation) — français + shikomori + arabe coranique simplifié.
5. **Politique de Confidentialité** — conforme loi comorienne 18-008 sur la protection des données personnelles + alignée RGPD pour la diaspora.
6. **Charte protection mineur** publique sur le site Nasoma.

### Statuts à envisager
- **Société d'exploitation Nasoma** : SARL ou SA comorienne, à créer (ou filiale 100 % de CK Innovation existante : SARL au capital 3 M KMF).
- **Filiale régionale** : envisageable à Maurice ou aux Seychelles pour la trésorerie offshore (mentionnée dans plan 2018).
- **Compte bancaire** : Comores + un compte offshore Maurice / Seychelles pour réserves USD.

### Conformité protection des données mineurs
- Aux Comores, la loi 18-008 sur la protection des données personnelles s'applique.
- Pour l'expansion régionale :
  - **Kenya** : Data Protection Act 2019 — enregistrement obligatoire ODPC.
  - **Tanzanie** : Personal Data Protection Act 2022.
  - **Rwanda** : Data Protection Law 2021.
  - **RDC** : pas encore de loi RGPD-like consolidée (anticiper le RGPD européen comme standard).
- Nomination d'un **DPO interne** (CK Innovation, Moroni) obligatoire dès le pilote.
- Consentement parental explicite horodaté + log d'audit pour chaque enfant < 13 ans.

---

## ANNEXE G — SPÉCIFICITÉS LANGUE & CULTURE COMORES

> Pour que l'IA codeuse adapte le produit au marché pilote comorien.

### Langues à intégrer (priorité décroissante)
1. **Français** (langue de scolarisation officielle, instruction et examens).
2. **Comorien (shikomori / shingazidja / shindzuani / shimaore)** — langue maternelle de 100 % de la population, **non écrite traditionnellement** (utilisée à l'oral et à la radio). C'est la langue **familiale**, la langue de **compréhension intuitive** pour les jeunes enfants.
3. **Arabe coranique** (école coranique / madrasa, fréquentée par > 80 % des enfants en parallèle du système classique).
4. **Anglais** (Y2+ : Kenya, Tanzanie).
5. **Swahili** (Y2+ : Kenya, Tanzanie, comprend les expatriés et communautés transfrontalières).

### Cas d'usage langue dans l'app
- **Interface utilisateur** : français par défaut (langue scolaire). Option shikomori en bouton de bascule (avec icônes pour les illettrés en français).
- **TTS / IA Vocale** : voix française + voix shikomori (synthétique à fine-tuner sur corpus radio comorienne ; OpenAI TTS et ElevenLabs supportent les voix multilingues).
- **Rapports SMS aux parents** : français par défaut, option shikomori transcrit phonétiquement (ex : *« Amina ka soma muhairi vyema »*).
- **Contenus pédagogiques** : générés en français (langue scolaire), explications audio possibles en shikomori.

### Considérations culturelles
- **Période scolaire comorienne** : Septembre → Juin (3 trimestres).
- **Période d'examens nationaux** : Mai-Juin (entrée 6ᵉ, BEPC, Baccalauréat). Pic d'usage attendu.
- **Ramadan** : usage potentiellement réduit, à anticiper dans les campagnes marketing.
- **Madrasa du matin** : beaucoup d'élèves vont à l'école coranique avant l'école laïque ; intégrer cette réalité dans les notifications horaires.
- **Polygamie et familles élargies** : un enfant peut avoir 2 mères / oncles co-payeurs → support multi-payeurs dans le compte famille.

### Diaspora — vecteur de croissance majeur
- **~300 000 Comoriens à l'étranger** (France, Mayotte, EAU, Madagascar).
- Ils sont les **premiers payeurs réels** des études des enfants restés au pays (transferts annuels Comores-Diaspora estimés à 15-20 % du PIB).
- Cible marketing à part entière : campagnes France/Mayotte ciblées sur la diaspora, avec paiement par carte bancaire européenne et virement automatique mensuel vers un compte enfant local.
- **Levier produit** : permettre à un oncle/tante en France de **suivre en direct** les progrès de son neveu/nièce à Moroni (push notifications + rapport hebdo + paiement direct depuis l'étranger).

---

## ANNEXE H — RECOMMANDATIONS PASEC INTÉGRÉES PAR DESIGN

> Le rapport PASEC 2010 a identifié les leviers d'amélioration scolaire. Nasoma transforme chacun en feature produit concrète.

| Levier PASEC (preuve scientifique) | Feature Nasoma associée |
|------------------------------------|-------------------------|
| Diminution du redoublement par meilleur suivi pédagogique | Profil de compétence BKT temps réel + alertes parents |
| Plus grande utilisation des manuels en classe | Scan de pages de manuel → exercices ciblés |
| Plus grande disponibilité des manuels à la maison | Bibliothèque numérique de fiches concept téléchargeables |
| Aide aux devoirs à la maison | Workflow scan-rattrapage le soir |
| Respect de la couverture du programme scolaire | Knowledge Graph aligné curriculum APC validé inspection |
| Alphabétisation des parents | IA vocale shikomori + rapports SMS pictographiques |
| Diminution du travail des enfants hors travail scolaire | Pas de gamification addictive : sessions courtes 10 min max |
| Présence des registres de retard et d'absence | Module F25-F28 (Track A LISEC) |
| Meilleur encadrement pédagogique par les directeurs | Dashboard école (heatmap des lacunes classe) |
| Formation à l'Approche Par Compétence (APC) | Curriculum comorien APC strictement respecté |
| Diminution des classes multigrades | Hors scope direct, mais Nasoma compense en personnalisant par élève |
| Proximité enseignant-élève | L'app sert de canal de communication directe parent-enseignant |

---

## ANNEXE I — CHECKLIST « ÉTAT D'AVANCEMENT » (à jour de mai 2026)

> Pour suivre la maturité du projet selon CK Innovation.

### Acquis (déjà réalisés)
- ✅ Vision produit définie
- ✅ Identité de marque Nasoma posée (« Mimi, Nasoma »)
- ✅ Dossiers stratégique + technique + commercial 2026 finalisés (13 slides chacun)
- ✅ Connaissance fine du marché comorien (10 ans CK Innovation)
- ✅ Réseau institutionnel comorien initié (NDA Commissariat 2018)
- ✅ Modèle économique validé sur précédent LISEC
- ✅ NDA template prêt pour partenariats nouveaux
- ✅ Étude de faisabilité OCR documentée

### À faire (court terme — 0 à 3 mois)
- [ ] Constituer l'équipe core (CTO, Mobile Lead, ML Engineer)
- [ ] Lever 200K $ pre-seed pour démarrage
- [ ] Mettre à jour NDA Commissariat Ngazidja (V2 Nasoma)
- [ ] Signer convention avec 3 écoles privées pilotes
- [ ] POC technique OCR sur 200 copies comoriennes
- [ ] Bootstrap repo + infrastructure dev
- [ ] Acquisition domaine nasoma.africa (et naso.ma)
- [ ] Création comptes AWS, Anthropic, OpenAI, GCP, Africa's Talking
- [ ] Préparation du Knowledge Graph CM1-CM2 avec inspecteur CIPR

### À faire (moyen terme — 3 à 9 mois)
- [ ] Application Android v1 (Tracks A+B) testée sur 3 écoles pilotes
- [ ] Intégration Hollo + Mvola opérationnelle
- [ ] 200-500 élèves comoriens en pilote
- [ ] Premières mesures de NPS et de Product-Market Fit
- [ ] Pitch deck investor-ready (sur la base du dossier stratégique consolidé existant)
- [ ] Levée seed 500K $-1M $

---

**FIN DU DOCUMENT**

*"Demain commence aujourd'hui."*
**Mimi, Nasoma.**

Pour toute question : `contact@nasoma.africa`
