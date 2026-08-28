"""Aesthetic module service layer.

Business logic for PhotoJourney, ConsultationNote, TreatmentHistory and
ProductRecommendation CRUD. Each method filters by clinic_id for
multi-tenancy and stamps the clinic_id/user_id from the authenticated
context — never from client-supplied data.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    ConsultationNote,
    PhotoJourney,
    ProductRecommendation,
    TreatmentHistory,
)


class AestheticService:
    """CRUD service for the aesthetic module entities."""

    # ------------------------------------------------------------------
    # PhotoJourney
    # ------------------------------------------------------------------

    @staticmethod
    async def list_photos(
        db: AsyncSession,
        clinic_id: UUID,
        *,
        patient_id: UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[PhotoJourney], int]:
        """List photo journeys for a clinic, optionally filtered by patient."""
        conditions = [PhotoJourney.clinic_id == clinic_id]
        if patient_id:
            conditions.append(PhotoJourney.patient_id == patient_id)

        total = (
            await db.execute(
                select(func.count(PhotoJourney.id)).where(*conditions)
            )
        ).scalar() or 0

        offset = (page - 1) * page_size
        result = await db.execute(
            select(PhotoJourney)
            .where(*conditions)
            .order_by(PhotoJourney.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    @staticmethod
    async def get_photo(
        db: AsyncSession, clinic_id: UUID, photo_id: UUID
    ) -> PhotoJourney | None:
        result = await db.execute(
            select(PhotoJourney).where(
                PhotoJourney.id == photo_id,
                PhotoJourney.clinic_id == clinic_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_photo(
        db: AsyncSession, clinic_id: UUID, data: dict
    ) -> PhotoJourney:
        photo = PhotoJourney(clinic_id=clinic_id, **data)
        db.add(photo)
        await db.flush()
        return photo

    @staticmethod
    async def update_photo(
        db: AsyncSession, photo: PhotoJourney, data: dict
    ) -> PhotoJourney:
        for key, value in data.items():
            setattr(photo, key, value)
        await db.flush()
        return photo

    @staticmethod
    async def delete_photo(db: AsyncSession, photo: PhotoJourney) -> None:
        await db.delete(photo)
        await db.flush()

    # ------------------------------------------------------------------
    # ConsultationNote
    # ------------------------------------------------------------------

    @staticmethod
    async def list_consultations(
        db: AsyncSession,
        clinic_id: UUID,
        *,
        patient_id: UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ConsultationNote], int]:
        conditions = [ConsultationNote.clinic_id == clinic_id]
        if patient_id:
            conditions.append(ConsultationNote.patient_id == patient_id)

        total = (
            await db.execute(
                select(func.count(ConsultationNote.id)).where(*conditions)
            )
        ).scalar() or 0

        offset = (page - 1) * page_size
        result = await db.execute(
            select(ConsultationNote)
            .where(*conditions)
            .order_by(ConsultationNote.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    @staticmethod
    async def get_consultation(
        db: AsyncSession, clinic_id: UUID, note_id: UUID
    ) -> ConsultationNote | None:
        result = await db.execute(
            select(ConsultationNote).where(
                ConsultationNote.id == note_id,
                ConsultationNote.clinic_id == clinic_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_consultation(
        db: AsyncSession, clinic_id: UUID, created_by: UUID, data: dict
    ) -> ConsultationNote:
        note = ConsultationNote(clinic_id=clinic_id, created_by=created_by, **data)
        db.add(note)
        await db.flush()
        return note

    @staticmethod
    async def update_consultation(
        db: AsyncSession, note: ConsultationNote, data: dict
    ) -> ConsultationNote:
        for key, value in data.items():
            setattr(note, key, value)
        await db.flush()
        return note

    @staticmethod
    async def delete_consultation(
        db: AsyncSession, note: ConsultationNote
    ) -> None:
        await db.delete(note)
        await db.flush()

    # ------------------------------------------------------------------
    # TreatmentHistory
    # ------------------------------------------------------------------

    @staticmethod
    async def list_treatments(
        db: AsyncSession,
        clinic_id: UUID,
        *,
        patient_id: UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[TreatmentHistory], int]:
        conditions = [TreatmentHistory.clinic_id == clinic_id]
        if patient_id:
            conditions.append(TreatmentHistory.patient_id == patient_id)

        total = (
            await db.execute(
                select(func.count(TreatmentHistory.id)).where(*conditions)
            )
        ).scalar() or 0

        offset = (page - 1) * page_size
        result = await db.execute(
            select(TreatmentHistory)
            .where(*conditions)
            .order_by(TreatmentHistory.performed_at.desc().nulls_last())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    @staticmethod
    async def get_treatment(
        db: AsyncSession, clinic_id: UUID, treatment_id: UUID
    ) -> TreatmentHistory | None:
        result = await db.execute(
            select(TreatmentHistory).where(
                TreatmentHistory.id == treatment_id,
                TreatmentHistory.clinic_id == clinic_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_treatment(
        db: AsyncSession, clinic_id: UUID, performed_by: UUID, data: dict
    ) -> TreatmentHistory:
        record = TreatmentHistory(
            clinic_id=clinic_id, performed_by=performed_by, **data
        )
        db.add(record)
        await db.flush()
        return record

    @staticmethod
    async def update_treatment(
        db: AsyncSession, record: TreatmentHistory, data: dict
    ) -> TreatmentHistory:
        for key, value in data.items():
            setattr(record, key, value)
        await db.flush()
        return record

    @staticmethod
    async def delete_treatment(
        db: AsyncSession, record: TreatmentHistory
    ) -> None:
        await db.delete(record)
        await db.flush()

    # ------------------------------------------------------------------
    # ProductRecommendation
    # ------------------------------------------------------------------

    @staticmethod
    async def list_recommendations(
        db: AsyncSession,
        clinic_id: UUID,
        *,
        patient_id: UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ProductRecommendation], int]:
        conditions = [ProductRecommendation.clinic_id == clinic_id]
        if patient_id:
            conditions.append(ProductRecommendation.patient_id == patient_id)

        total = (
            await db.execute(
                select(func.count(ProductRecommendation.id)).where(*conditions)
            )
        ).scalar() or 0

        offset = (page - 1) * page_size
        result = await db.execute(
            select(ProductRecommendation)
            .where(*conditions)
            .order_by(ProductRecommendation.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    @staticmethod
    async def get_recommendation(
        db: AsyncSession, clinic_id: UUID, rec_id: UUID
    ) -> ProductRecommendation | None:
        result = await db.execute(
            select(ProductRecommendation).where(
                ProductRecommendation.id == rec_id,
                ProductRecommendation.clinic_id == clinic_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_recommendation(
        db: AsyncSession, clinic_id: UUID, prescribed_by: UUID, data: dict
    ) -> ProductRecommendation:
        rec = ProductRecommendation(
            clinic_id=clinic_id, prescribed_by=prescribed_by, **data
        )
        db.add(rec)
        await db.flush()
        return rec

    @staticmethod
    async def update_recommendation(
        db: AsyncSession, rec: ProductRecommendation, data: dict
    ) -> ProductRecommendation:
        for key, value in data.items():
            setattr(rec, key, value)
        await db.flush()
        return rec

    @staticmethod
    async def delete_recommendation(
        db: AsyncSession, rec: ProductRecommendation
    ) -> None:
        await db.delete(rec)
        await db.flush()