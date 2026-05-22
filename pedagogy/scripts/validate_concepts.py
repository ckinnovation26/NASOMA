"""Valide l'intégrité du knowledge graph (DAG, codes uniques, prerequisites valides).

Format Annexe E BP : metadata + concepts (code, name, difficulty 1-5,
estimated_minutes, prerequisites, curriculum_refs, common_errors structurés).

Usage:
    python -m pedagogy.scripts.validate_concepts pedagogy/apc_km/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_METADATA = {"country", "curriculum_code", "subject", "grade_level", "version"}
REQUIRED_FIELDS = {
    "code",
    "name",
    "difficulty",
    "estimated_minutes",
    "prerequisites",
    "curriculum_refs",
    "description",
}

VALID_SUBJECTS = {"MATH", "FR", "AR", "SCI"}
VALID_GRADES = {"CM1", "CM2", "6E"}


def load_all(directory: Path) -> dict[str, dict]:
    """Charge tous les concepts en un dict {code: concept}, valide la metadata."""
    all_concepts: dict[str, dict] = {}
    duplicates: list[str] = []
    metadata_errors: list[str] = []

    for json_file in sorted(directory.glob("*.json")):
        with json_file.open(encoding="utf-8") as f:
            data = json.load(f)

        meta = data.get("metadata", {})
        missing_meta = REQUIRED_METADATA - set(meta.keys())
        if missing_meta:
            metadata_errors.append(f"  • {json_file.name} → metadata manquante: {missing_meta}")
        if meta.get("subject") not in VALID_SUBJECTS:
            metadata_errors.append(f"  • {json_file.name} → subject invalide: {meta.get('subject')}")
        if meta.get("grade_level") not in VALID_GRADES:
            metadata_errors.append(f"  • {json_file.name} → grade_level invalide: {meta.get('grade_level')}")

        for concept in data.get("concepts", []):
            code = concept.get("code")
            if code in all_concepts:
                duplicates.append(code)
            all_concepts[code] = concept

    if metadata_errors:
        print("❌ Erreurs metadata:", file=sys.stderr)
        print("\n".join(metadata_errors), file=sys.stderr)
        sys.exit(1)

    if duplicates:
        print(f"❌ Codes en doublon: {duplicates}", file=sys.stderr)
        sys.exit(1)

    return all_concepts


def check_required_fields(concepts: dict[str, dict]) -> list[str]:
    errors = []
    for code, c in concepts.items():
        missing = REQUIRED_FIELDS - set(c.keys())
        if missing:
            errors.append(f"  • {code} → champs manquants: {missing}")
    return errors


def check_difficulty(concepts: dict[str, dict]) -> list[str]:
    errors = []
    for code, c in concepts.items():
        d = c.get("difficulty")
        if not isinstance(d, int) or not 1 <= d <= 5:
            errors.append(f"  • {code} → difficulty invalide ({d}) — attendu 1..5")
    return errors


def check_prerequisites(concepts: dict[str, dict]) -> list[str]:
    """Vérifie que tous les prerequisites pointent vers des codes existants
    OU vers des codes de classes inférieures (qui seront seedés ailleurs)."""
    errors = []
    codes = set(concepts.keys())
    for code, c in concepts.items():
        for prereq in c.get("prerequisites", []):
            # Si le prereq commence par MATH_CM1_ et qu'on est en CM2, on tolère
            # (les CM1 seront seedés dans leur propre fichier)
            if prereq not in codes:
                # Heuristique : tolérer si c'est un prérequis de classe inférieure
                # (on validera lors du seed global cross-fichiers)
                if not (
                    prereq.startswith(("MATH_CM1_", "FR_CM1_", "AR_CM1_"))
                    or prereq.startswith(("MATH_CM2_", "FR_CM2_"))  # pour les 6E
                ):
                    errors.append(f"  • {code} → prerequisite inconnu: {prereq}")
    return errors


def check_common_errors_format(concepts: dict[str, dict]) -> list[str]:
    """Vérifie que common_errors est bien un array d'objets {code, description}."""
    errors = []
    for code, c in concepts.items():
        ce = c.get("common_errors", [])
        if not isinstance(ce, list):
            errors.append(f"  • {code} → common_errors doit être un array")
            continue
        for i, err in enumerate(ce):
            if not isinstance(err, dict):
                errors.append(f"  • {code}.common_errors[{i}] → doit être un objet")
                continue
            if "code" not in err or "description" not in err:
                errors.append(f"  • {code}.common_errors[{i}] → manque code ou description")
    return errors


def check_no_cycles(concepts: dict[str, dict]) -> list[str]:
    """Détecte les cycles dans le DAG par parcours DFS."""
    errors: list[str] = []
    WHITE, GRAY, BLACK = 0, 1, 2
    colors = {code: WHITE for code in concepts}

    def visit(code: str, path: list[str]) -> bool:
        colors[code] = GRAY
        for prereq in concepts[code].get("prerequisites", []):
            if prereq not in concepts:
                continue   # ignoré (cross-fichier, validé ailleurs)
            if colors[prereq] == GRAY:
                errors.append(f"  • Cycle: {' → '.join(path + [code, prereq])}")
                return False
            if colors[prereq] == WHITE and not visit(prereq, path + [code]):
                return False
        colors[code] = BLACK
        return True

    for code in concepts:
        if colors[code] == WHITE:
            visit(code, [])

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the knowledge graph (BP Annexe E).")
    parser.add_argument("directory", type=Path, help="Dossier contenant les .json")
    args = parser.parse_args()

    if not args.directory.is_dir():
        print(f"❌ Dossier introuvable: {args.directory}", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Validation du knowledge graph (Annexe E BP) dans {args.directory}")
    concepts = load_all(args.directory)
    print(f"   {len(concepts)} concept(s) chargé(s)")

    all_errors: list[str] = []
    for check_name, check_fn in [
        ("Champs requis", check_required_fields),
        ("Difficulty 1..5", check_difficulty),
        ("common_errors format {code, description}", check_common_errors_format),
        ("Prerequisites valides", check_prerequisites),
        ("Pas de cycle dans le DAG", check_no_cycles),
    ]:
        errs = check_fn(concepts)
        status = "✅" if not errs else "❌"
        print(f"{status} {check_name}: {len(errs)} erreur(s)")
        all_errors.extend(errs)

    if all_errors:
        print("\n".join(all_errors), file=sys.stderr)
        sys.exit(1)

    print(f"\n✨ Validation réussie — {len(concepts)} concepts cohérents.")


if __name__ == "__main__":
    main()
