"""Service Indicateurs CT/MT/LT — cœur de valeur produit Nasoma.

Stratégie (cf. docs/strategie_Nasoma.md) :
- CT (court terme, J+1) : "Aujourd'hui, Ali a buté sur les retenues — 3 exos demain"
- MT (moyen terme, semaine/mois) : ajustement routine
- LT (long terme, trimestre/année) : décision pédagogique (orientation, soutien)

Workflow :
1. Cron quotidien 02:00 locale → `compute_daily_snapshots()` enregistre les mastery
2. Cron quotidien 02:15 locale → `compute_indicators_for_all_active_students()` agrège
3. Les endpoints servent depuis la table `student_indicators` (cache pré-calculé)
"""

from __future__ import annotations

import statistics
import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

import structlog
from sqlalchemy import and_, delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.concepts import Concept
from app.models.indicators import (
    IndicatorHorizon,
    MasterySnapshot,
    StudentIndicators,
)
from app.models.mastery import StudentConceptMastery
from app.models.scans import Scan, ScanStatus
from app.models.users import AccountState, User

logger = structlog.get_logger(__name__)


# Seuils de statut BKT (cf. bkt_service.py)
THRESHOLD_MASTERED = 0.85
THRESHOLD_IN_PROGRESS = 0.50


@dataclass(frozen=True)
class IndicatorView:
    """Réponse API enrichie."""

    horizon: IndicatorHorizon
    period_start: date
    period_end: date
    metrics: dict
    recommendations: list


class IndicatorsService:
    """Calcul et exposition des indicateurs CT/MT/LT."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ──────────────────────────────────────────────
    #  Cron 1 — snapshot quotidien BKT
    # ──────────────────────────────────────────────
    async def compute_daily_snapshots(
        self, target_date: date | None = None
    ) -> int:
        """Capture l'état BKT actuel de chaque (student, concept) actif.

        À lancer chaque nuit. Idempotent : ON CONFLICT replace.
        """
        if target_date is None:
            target_date = datetime.now(UTC).date()

        stmt = select(
            StudentConceptMastery.student_id,
            StudentConceptMastery.concept_id,
            StudentConceptMastery.tenant_id,
            StudentConceptMastery.mastery_probability,
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        count = 0
        for row in rows:
            ins = insert(MasterySnapshot).values(
                student_id=row[0],
                concept_id=row[1],
                snapshot_date=target_date,
                tenant_id=row[2],
                mastery_probability=row[3],
            )
            ins = ins.on_conflict_do_update(
                index_elements=["student_id", "concept_id", "snapshot_date"],
                set_={"mastery_probability": row[3]},
            )
            await self.db.execute(ins)
            count += 1

        await self.db.flush()
        logger.info("indicators.snapshots_captured", date=str(target_date), count=count)
        return count

    # ──────────────────────────────────────────────
    #  Cron 2 — agrégation indicateurs CT/MT/LT
    # ──────────────────────────────────────────────
    async def compute_indicators_for_student(
        self, student_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> dict[IndicatorHorizon, StudentIndicators]:
        """Calcule les 3 horizons pour un user et persiste."""
        today = datetime.now(UTC).date()

        ct = await self._compute_ct(student_id, tenant_id, today)
        mt = await self._compute_mt(student_id, tenant_id, today)
        lt = await self._compute_lt(student_id, tenant_id, today)

        # Idempotent : remplacer l'ancien indicateur du jour
        await self.db.execute(
            delete(StudentIndicators).where(
                StudentIndicators.student_id == student_id,
                StudentIndicators.computed_at >= datetime.combine(today, datetime.min.time(), tzinfo=UTC),
            )
        )
        self.db.add_all([ct, mt, lt])
        await self.db.flush()
        return {IndicatorHorizon.CT: ct, IndicatorHorizon.MT: mt, IndicatorHorizon.LT: lt}

    async def compute_for_all_active_students(self) -> int:
        """Cron job — pour tous les comptes ACTIVE."""
        stmt = select(User.id, User.tenant_id).where(
            User.account_state == AccountState.ACTIVE
        )
        result = await self.db.execute(stmt)
        users = result.all()

        for user_id, tenant_id in users:
            try:
                await self.compute_indicators_for_student(user_id, tenant_id)
            except Exception as e:
                logger.error(
                    "indicators.compute_failed",
                    user_id=str(user_id),
                    error=str(e),
                )

        await self.db.commit()
        logger.info("indicators.batch_complete", count=len(users))
        return len(users)

    # ──────────────────────────────────────────────
    #  Endpoints — lecture indicateurs
    # ──────────────────────────────────────────────
    async def get_latest(
        self, student_id: uuid.UUID, horizon: IndicatorHorizon
    ) -> StudentIndicators | None:
        """Retourne le dernier indicateur calculé pour un horizon donné."""
        stmt = (
            select(StudentIndicators)
            .where(
                StudentIndicators.student_id == student_id,
                StudentIndicators.horizon == horizon,
            )
            .order_by(StudentIndicators.computed_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_trajectory(
        self,
        student_id: uuid.UUID,
        subject_code: str | None = None,
        days: int = 90,
    ) -> list[dict]:
        """Série temporelle BKT moyenne pour graphique."""
        cutoff = datetime.now(UTC).date() - timedelta(days=days)

        # Moyenne BKT par jour
        stmt = (
            select(
                MasterySnapshot.snapshot_date,
                func.avg(MasterySnapshot.mastery_probability).label("avg"),
            )
            .where(
                MasterySnapshot.student_id == student_id,
                MasterySnapshot.snapshot_date >= cutoff,
            )
            .group_by(MasterySnapshot.snapshot_date)
            .order_by(MasterySnapshot.snapshot_date.asc())
        )
        if subject_code:
            stmt = stmt.join(Concept, Concept.id == MasterySnapshot.concept_id).where(
                Concept.subject.has(code=subject_code)  # noqa: E501
            )

        result = await self.db.execute(stmt)
        return [
            {"date": row[0].isoformat(), "mastery_avg": round(float(row[1]), 3)}
            for row in result.all()
        ]

    async def get_daily_recommendations(
        self, student_id: uuid.UUID
    ) -> list[dict]:
        """Recommandations d'action pour J+1 (extrait de l'indicateur CT)."""
        ct = await self.get_latest(student_id, IndicatorHorizon.CT)
        return list(ct.recommendations) if ct else []

    # ──────────────────────────────────────────────
    #  Helpers — calcul par horizon
    # ──────────────────────────────────────────────
    async def _compute_ct(
        self, student_id: uuid.UUID, tenant_id: uuid.UUID, today: date
    ) -> StudentIndicators:
        """Court terme : focus sur la journée d'hier (delta) et concept bloqué."""
        yesterday = today - timedelta(days=1)

        # Concepts pratiqués aujourd'hui (via session_answers de la journée)
        # Simplifié pour MVP : on regarde les masteries dont last_practiced_at = today
        today_start = datetime.combine(today, datetime.min.time(), tzinfo=UTC)
        mastery_stmt = select(StudentConceptMastery).where(
            StudentConceptMastery.student_id == student_id,
            StudentConceptMastery.last_practiced_at >= today_start,
        )
        masteries_today_result = await self.db.execute(mastery_stmt)
        masteries_today = list(masteries_today_result.scalars().all())

        # Moyenne du jour
        avg_today = (
            statistics.mean([m.mastery_probability for m in masteries_today])
            if masteries_today
            else None
        )

        # Delta vs hier
        snap_yesterday_stmt = select(MasterySnapshot.mastery_probability).where(
            MasterySnapshot.student_id == student_id,
            MasterySnapshot.snapshot_date == yesterday,
        )
        snap_yesterday_result = await self.db.execute(snap_yesterday_stmt)
        snaps_yesterday = [r[0] for r in snap_yesterday_result.all()]
        avg_yesterday = statistics.mean(snaps_yesterday) if snaps_yesterday else None
        delta = (
            round(avg_today - avg_yesterday, 3)
            if (avg_today is not None and avg_yesterday is not None)
            else None
        )

        # Concept le plus bloqué (le plus faible)
        blocked = await self._find_weakest_concept(student_id)

        metrics = {
            "concepts_practiced_today": len(masteries_today),
            "mastery_avg_today": round(avg_today, 3) if avg_today is not None else None,
            "delta_vs_yesterday": delta,
            "blocked_concept": blocked["code"] if blocked else None,
        }

        recommendations = []
        if blocked:
            recommendations.append(
                {
                    "action": "exercise_session",
                    "target_concept_code": blocked["code"],
                    "rationale": (
                        f"Concept le plus faible ({round(blocked['p'] * 100)} % de maîtrise) — "
                        "à travailler en priorité demain"
                    ),
                    "duration_minutes": 10,
                }
            )

        return StudentIndicators(
            tenant_id=tenant_id,
            student_id=student_id,
            horizon=IndicatorHorizon.CT,
            period_start=today,
            period_end=today,
            metrics=metrics,
            recommendations=recommendations,
        )

    async def _compute_mt(
        self, student_id: uuid.UUID, tenant_id: uuid.UUID, today: date
    ) -> StudentIndicators:
        """Moyen terme : tendance sur 30 derniers jours."""
        period_start = today - timedelta(days=30)

        # Concepts acquis (mastery > 0.85) durant la période
        acquired_stmt = select(func.count()).select_from(StudentConceptMastery).where(
            StudentConceptMastery.student_id == student_id,
            StudentConceptMastery.mastery_probability >= THRESHOLD_MASTERED,
            StudentConceptMastery.last_practiced_at
            >= datetime.combine(period_start, datetime.min.time(), tzinfo=UTC),
        )
        concepts_acquired = (await self.db.execute(acquired_stmt)).scalar_one() or 0

        blocked_stmt = select(func.count()).select_from(StudentConceptMastery).where(
            StudentConceptMastery.student_id == student_id,
            StudentConceptMastery.mastery_probability < THRESHOLD_IN_PROGRESS,
            StudentConceptMastery.failures_last_7_days >= 2,
        )
        concepts_blocked = (await self.db.execute(blocked_stmt)).scalar_one() or 0

        # Pente trend : régression linéaire simple sur la moyenne BKT par jour
        traj = await self.get_trajectory(student_id, days=30)
        slope = self._linear_slope([(i, p["mastery_avg"]) for i, p in enumerate(traj)])

        # Fréquence scans par semaine
        scan_count_stmt = select(func.count()).select_from(Scan).where(
            Scan.student_id == student_id,
            Scan.status.in_([ScanStatus.DONE, ScanStatus.DONE_WITH_FALLBACK]),
            Scan.created_at
            >= datetime.combine(period_start, datetime.min.time(), tzinfo=UTC),
        )
        scans_30d = (await self.db.execute(scan_count_stmt)).scalar_one() or 0
        scan_freq_per_week = round((scans_30d / 30) * 7, 2)

        metrics = {
            "concepts_acquired": concepts_acquired,
            "concepts_blocked": concepts_blocked,
            "mastery_trend_slope": slope,
            "scan_frequency_per_week": scan_freq_per_week,
        }

        recommendations = []
        if slope is not None and slope < 0:
            recommendations.append(
                {
                    "action": "raise_engagement",
                    "rationale": "Tendance maîtrise en baisse sur 30 jours — augmenter la fréquence",
                    "minutes_per_day": 15,
                }
            )
        if scan_freq_per_week < 2:
            recommendations.append(
                {
                    "action": "encourage_scan",
                    "rationale": "Moins de 2 scans/semaine — encourager le rythme régulier",
                }
            )

        return StudentIndicators(
            tenant_id=tenant_id,
            student_id=student_id,
            horizon=IndicatorHorizon.MT,
            period_start=period_start,
            period_end=today,
            metrics=metrics,
            recommendations=recommendations,
        )

    async def _compute_lt(
        self, student_id: uuid.UUID, tenant_id: uuid.UUID, today: date
    ) -> StudentIndicators:
        """Long terme : trimestre + projections curriculum."""
        period_start = today - timedelta(days=90)

        all_masteries_stmt = select(StudentConceptMastery).where(
            StudentConceptMastery.student_id == student_id
        )
        masteries = list(
            (await self.db.execute(all_masteries_stmt)).scalars().all()
        )

        acquired_total = sum(
            1 for m in masteries if m.mastery_probability >= THRESHOLD_MASTERED
        )

        # Estimation concepts restants : on prend le grade_level de l'user
        user = await self.db.get(User, student_id)
        grade = user.grade_level if user else None
        remaining_stmt = select(func.count()).select_from(Concept).where(
            Concept.grade_level == grade
        ) if grade else select(func.count()).select_from(Concept)
        total_curriculum = (await self.db.execute(remaining_stmt)).scalar_one() or 0
        concepts_remaining = max(0, total_curriculum - acquired_total)

        # Projection date de complétion linéaire (basée sur la trend MT)
        projected_completion = None
        # Détection de blocages chroniques (failures > 4 sur 7 jours)
        risk_flags = []
        chronic_block_stmt = select(StudentConceptMastery).where(
            StudentConceptMastery.student_id == student_id,
            StudentConceptMastery.failures_last_7_days >= 4,
        )
        chronic_blocks = list(
            (await self.db.execute(chronic_block_stmt)).scalars().all()
        )
        for cb in chronic_blocks:
            concept = await self.db.get(Concept, cb.concept_id)
            if concept:
                risk_flags.append(f"persistent:{concept.code}")

        metrics = {
            "concepts_acquired_total": acquired_total,
            "concepts_remaining_curriculum": concepts_remaining,
            "projected_completion_date": projected_completion,
            "risk_flags": risk_flags,
        }

        recommendations = []
        if risk_flags:
            recommendations.append(
                {
                    "action": "pedagogical_decision",
                    "target": risk_flags[0].split(":", 1)[1],
                    "rationale": (
                        "Blocage chronique détecté (≥4 échecs en 7 jours). "
                        "Risque de redoublement si non traité. "
                        "Envisager soutien renforcé ou accompagnement humain."
                    ),
                    "priority": "high",
                }
            )

        return StudentIndicators(
            tenant_id=tenant_id,
            student_id=student_id,
            horizon=IndicatorHorizon.LT,
            period_start=period_start,
            period_end=today,
            metrics=metrics,
            recommendations=recommendations,
        )

    async def _find_weakest_concept(
        self, student_id: uuid.UUID
    ) -> dict | None:
        stmt = (
            select(StudentConceptMastery, Concept.code)
            .join(Concept, Concept.id == StudentConceptMastery.concept_id)
            .where(StudentConceptMastery.student_id == student_id)
            .order_by(StudentConceptMastery.mastery_probability.asc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if row is None:
            return None
        mastery, code = row
        return {"code": code, "p": mastery.mastery_probability}

    @staticmethod
    def _linear_slope(points: list[tuple[int, float]]) -> float | None:
        """Régression linéaire simple — pente de la trend."""
        if len(points) < 2:
            return None
        n = len(points)
        sum_x = sum(p[0] for p in points)
        sum_y = sum(p[1] for p in points)
        sum_xy = sum(p[0] * p[1] for p in points)
        sum_x2 = sum(p[0] ** 2 for p in points)
        denom = n * sum_x2 - sum_x ** 2
        if denom == 0:
            return None
        return round((n * sum_xy - sum_x * sum_y) / denom, 4)
