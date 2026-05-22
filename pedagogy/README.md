# Nasoma — Knowledge Graph pédagogique (APC Comores)

Source de vérité du **cerveau pédagogique** de Nasoma : ~650 concepts répartis sur 4 matières et 3 niveaux, alignés sur le curriculum **APC** (Approche Par Compétences) du Plan Directeur de l'Éducation comorien 2010-2015.

> Format aligné sur l'Annexe E du Business Plan (mai 2026).

## Volume cible MVP

| Matière | Niveau | Concepts cibles | Priorité |
|---|---|---|---|
| Mathématiques | CM1 | ~80 | **P0** |
| Mathématiques | CM2 | ~100 | **P0** |
| Français | CM1 | ~80 | **P0** |
| Français | CM2 | ~100 | **P0** |
| Mathématiques | 6ᵉ | ~100 | P1 |
| Français | 6ᵉ | ~80 | P1 |
| Arabe coranique | CM1-CM2 | ~50 | P1 (différenciateur Comores) |
| Sciences | CM2 | ~60 | P2 |
| **TOTAL seed initial MVP** | | **~650** | |

## Format d'un fichier JSON (Annexe E BP)

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
      "description": "Effectuer une addition de nombres à 3 chiffres avec retenue.",
      "common_errors": [
        {"code": "missing_carry", "description": "Oubli de la retenue en colonne suivante"},
        {"code": "wrong_column", "description": "Retenue placée dans la mauvaise colonne"}
      ]
    }
  ]
}
```

### Champs obligatoires

| Champ | Type | Description |
|---|---|---|
| `code` | string | Identifiant unique (cf. naming convention ci-dessous) |
| `name` | string | Nom en français |
| `difficulty` | integer 1-5 | 1=facile, 5=complexe |
| `estimated_minutes` | integer | Durée estimée pour maîtriser |
| `prerequisites` | array<string> | Liste des `code` requis (DAG) |
| `curriculum_refs` | object | `{"APC_KM": "M.x.y.z", "PASEC": "..."}` |
| `description` | string | 1-2 phrases en français |

### Champs optionnels mais recommandés

| Champ | Type | Description |
|---|---|---|
| `name_shikomori` | string | Traduction shikomori (différenciateur Comores) |
| `name_swahili` | string | Traduction swahili |
| `name_arabic` | string | Traduction arabe (pour matière Arabe coranique) |
| `common_errors` | array<object> | `[{"code": "...", "description": "..."}]` |
| `example_exercise` | string | Exercice exemple |
| `tts_pronunciation_fr` | string | Texte pour TTS français |
| `tts_pronunciation_shk` | string | Texte pour TTS shikomori |

## Naming convention `code`

```
{SUBJECT}_{GRADE}_{TOPIC}
```

- `SUBJECT` : `MATH` | `FR` | `AR` | `SCI`
- `GRADE` : `CM1` | `CM2` | `6E`
- `TOPIC` : court, en MAJUSCULES_SOULIGNÉES, ≤ 30 chars

Exemples (cf. BP) :
- `MATH_CM2_ADD_RETENUE`
- `MATH_CM2_MULT_2DIGITS`
- `MATH_CM2_FRAC_EQUIV`
- `FR_CM1_CONJ_PRESENT_ER`
- `AR_CM2_LECTURE_FATIHA`
- `SCI_CM2_VIVANT_CYCLE_EAU`

## Méthodologie de génération (Annexe E BP §5)

1. **Ingérer** les programmes officiels APC Comores (à scanner / OCRiser via l'app elle-même !).
2. **Générer** une première liste exhaustive de concepts par classe-matière via LLM Gemini (prompt template fourni dans `scripts/generate_concepts.py`).
3. **Annoter** les prérequis (DAG) en croisant avec les programmes des classes inférieures.
4. **Faire valider** par un comité pédagogique de 3 inspecteurs CIPR rémunérés (300-500 € forfait).
5. **Bulk-insert** dans la base via script Alembic `seed_concepts.py`.

## Validation automatique

Avant tout seed en base, lancer :

```bash
python -m pedagogy.scripts.validate_concepts pedagogy/apc_km/
```

Critères vérifiés :
- `code` unique dans tout le graphe
- Tous les `prerequisites` référencent des codes existants ou de classes inférieures
- Pas de cycle dans le DAG
- Champs obligatoires présents
- `grade_level` cohérent avec le code
- `difficulty` ∈ [1, 5]
- `curriculum_refs` contient au moins une clé valide

## Seed en base

```bash
cd backend
python -m pedagogy.scripts.seed_concepts \
  --curriculum APC_KM_2010 \
  --file ../pedagogy/apc_km/math_cm2.json
```

## Structure des fichiers

```
pedagogy/
├── apc_km/                       Curriculum Comores (Annexe E BP)
│   ├── math_cm1.json             P0 — 80 concepts
│   ├── math_cm2.json             P0 — 100 concepts
│   ├── math_6e.json              P1 — 100 concepts
│   ├── francais_cm1.json         P0 — 80 concepts
│   ├── francais_cm2.json         P0 — 100 concepts
│   ├── francais_6e.json          P1 — 80 concepts
│   ├── arabe_cm1.json            P1 — partiel
│   ├── arabe_cm2.json            P1 — partiel (total Arabe ~50)
│   └── sciences_cm2.json         P2 — 60 concepts
├── scripts/
│   ├── seed_concepts.py          Charge en Postgres
│   ├── validate_concepts.py      Vérifie l'intégrité du DAG
│   └── generate_concepts.py      Génère via Gemini Flash-8B
└── README.md
```
