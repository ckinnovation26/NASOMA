"""Tests PaymentService — initiate, providers, webhook → activation."""

from __future__ import annotations

import pytest

from app.services.payment_service import (
    PLAN_DURATION_DAYS,
    PLAN_PRICING_KMF,
    PLAN_SCANS,
)
from app.models.subscriptions import SubscriptionPlan


def test_pricing_table_matches_business_decision() -> None:
    """Le tarif doit matcher les décisions verrouillées."""
    assert PLAN_PRICING_KMF[SubscriptionPlan.DAILY] == 100
    assert PLAN_PRICING_KMF[SubscriptionPlan.THREE_DAY] == 250
    assert PLAN_PRICING_KMF[SubscriptionPlan.WEEKLY] == 500
    assert PLAN_PRICING_KMF[SubscriptionPlan.MONTHLY_PER_CHILD] == 1500


def test_scans_quota_matches_business() -> None:
    assert PLAN_SCANS[SubscriptionPlan.DAILY] == 5
    assert PLAN_SCANS[SubscriptionPlan.THREE_DAY] == 15
    assert PLAN_SCANS[SubscriptionPlan.WEEKLY] == 30
    assert PLAN_SCANS[SubscriptionPlan.MONTHLY_PER_CHILD] == 120


def test_duration_matches_plan_naming() -> None:
    assert PLAN_DURATION_DAYS[SubscriptionPlan.DAILY] == 1
    assert PLAN_DURATION_DAYS[SubscriptionPlan.THREE_DAY] == 3
    assert PLAN_DURATION_DAYS[SubscriptionPlan.WEEKLY] == 7
    assert PLAN_DURATION_DAYS[SubscriptionPlan.MONTHLY_PER_CHILD] == 30


def test_unit_economics_three_day_better_than_daily() -> None:
    """Le plan 3 jours doit avoir un meilleur ratio prix/scan que le journalier."""
    daily_per_scan = PLAN_PRICING_KMF[SubscriptionPlan.DAILY] / PLAN_SCANS[SubscriptionPlan.DAILY]
    three_day_per_scan = (
        PLAN_PRICING_KMF[SubscriptionPlan.THREE_DAY]
        / PLAN_SCANS[SubscriptionPlan.THREE_DAY]
    )
    assert three_day_per_scan < daily_per_scan


def test_monthly_cheapest_per_scan() -> None:
    """Le mensuel par enfant doit être le meilleur tarif par scan."""
    rates = {
        plan: PLAN_PRICING_KMF[plan] / PLAN_SCANS[plan]
        for plan in PLAN_PRICING_KMF
    }
    min_plan = min(rates, key=rates.get)
    assert min_plan == SubscriptionPlan.MONTHLY_PER_CHILD
