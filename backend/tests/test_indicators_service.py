"""Tests Indicateurs CT/MT/LT — formules + calculs."""

from __future__ import annotations

from app.services.indicators_service import IndicatorsService


def test_linear_slope_increasing() -> None:
    """Trend croissante → pente positive."""
    points = [(0, 0.1), (1, 0.2), (2, 0.3), (3, 0.4), (4, 0.5)]
    slope = IndicatorsService._linear_slope(points)
    assert slope is not None
    assert slope > 0
    assert abs(slope - 0.1) < 0.001


def test_linear_slope_decreasing() -> None:
    """Trend décroissante → pente négative."""
    points = [(0, 0.5), (1, 0.4), (2, 0.3), (3, 0.2)]
    slope = IndicatorsService._linear_slope(points)
    assert slope is not None
    assert slope < 0


def test_linear_slope_flat() -> None:
    """Pas de tendance → pente ~0."""
    points = [(0, 0.5), (1, 0.5), (2, 0.5)]
    slope = IndicatorsService._linear_slope(points)
    assert slope is not None
    assert abs(slope) < 0.0001


def test_linear_slope_insufficient_points() -> None:
    """Moins de 2 points → None."""
    assert IndicatorsService._linear_slope([]) is None
    assert IndicatorsService._linear_slope([(0, 0.5)]) is None


def test_linear_slope_constant_x() -> None:
    """Tous les x identiques → division par 0 → None."""
    points = [(0, 0.1), (0, 0.2), (0, 0.3)]
    assert IndicatorsService._linear_slope(points) is None
