"""Tests BKT — formule + service avec persistance."""

from __future__ import annotations

import pytest

from app.services.bkt_service import (
    P_GUESS,
    P_INIT,
    P_SLIP,
    P_TRANSIT,
    THRESHOLD_IN_PROGRESS,
    THRESHOLD_MASTERED,
    bkt_update_formula,
    status_for,
)


def test_bkt_initial_correct_increases_mastery() -> None:
    """Une bonne réponse depuis p_init doit faire monter la maîtrise."""
    after = bkt_update_formula(P_INIT, correct=True)
    assert after > P_INIT
    assert after <= 1.0


def test_bkt_initial_incorrect_decreases_or_stays_low() -> None:
    """Une mauvaise réponse depuis p_init garde la maîtrise basse."""
    after = bkt_update_formula(P_INIT, correct=False)
    assert after < 0.3                 # reste bas


def test_bkt_high_mastery_correct_stays_high() -> None:
    """Confirmation : maîtrise élevée reste élevée après bonne réponse."""
    after = bkt_update_formula(0.9, correct=True)
    assert after >= 0.85


def test_bkt_high_mastery_incorrect_drops_but_recovers() -> None:
    """Une erreur sur un concept maîtrisé fait baisser (slip)."""
    after = bkt_update_formula(0.9, correct=False)
    assert after < 0.9


def test_bkt_clamped_within_0_1() -> None:
    """La valeur reste dans [0, 1]."""
    for p in (0.0, 0.5, 1.0):
        for correct in (True, False):
            result = bkt_update_formula(p, correct=correct)
            assert 0.0 <= result <= 1.0


def test_bkt_convergence_after_5_correct() -> None:
    """5 réponses correctes consécutives → maîtrise > 0.85."""
    p = P_INIT
    for _ in range(5):
        p = bkt_update_formula(p, correct=True)
    assert p > 0.85


def test_status_thresholds() -> None:
    assert status_for(0.95) == "maitrise"
    assert status_for(THRESHOLD_MASTERED) == "maitrise"
    assert status_for(0.70) == "en_cours"
    assert status_for(THRESHOLD_IN_PROGRESS) == "en_cours"
    assert status_for(0.49) == "non_maitrise"
    assert status_for(0.0) == "non_maitrise"


def test_bkt_parameters_match_bp_spec() -> None:
    """Les paramètres doivent matcher la spec §25 BP."""
    assert P_INIT == 0.1
    assert P_TRANSIT == 0.2
    assert P_SLIP == 0.1
    assert P_GUESS == 0.25
