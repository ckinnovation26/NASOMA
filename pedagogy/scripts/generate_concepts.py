"""Génère un premier jet de concepts via Gemini (à valider par un pédagogue).

Usage:
    python -m pedagogy.scripts.generate_concepts \
        --subject math \
        --grade CM2 \
        --curriculum APC_KM \
        --output pedagogy/apc_km/math_cm2.draft.json

⚠️ Le fichier généré sort en *.draft.json — un humain DOIT relire et renommer.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Génère un draft de concepts via Gemini (à valider humain).",
    )
    parser.add_argument("--subject", required=True, choices=["math", "francais", "arabe", "sciences"])
    parser.add_argument("--grade", required=True, choices=["CM1", "CM2", "6E"])
    parser.add_argument("--curriculum", default="APC_KM")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--target-count", type=int, default=50)
    args = parser.parse_args()

    # TODO Sprint 1 :
    # 1. Charger le Plan Directeur Éducation Comores (PDF → markdown)
    # 2. Appel Gemini 1.5 Flash-8B avec responseSchema strict
    # 3. Génération itérative par batch de 20 concepts
    # 4. Sauvegarde en *.draft.json (jamais écraser le validé)

    print(f"📝 Génération draft : {args.subject} {args.grade} ({args.target_count} concepts cible)")
    print(f"   → {args.output}")
    print("⚠️  Implémentation Gemini à finaliser (Sprint 1).")
    print("⚠️  Tout draft DOIT être relu par un enseignant comorien avant validation.")


if __name__ == "__main__":
    main()
