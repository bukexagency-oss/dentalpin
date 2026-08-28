"""HTTP surface for the aesthetic module.

Mounted under ``/api/v1/aesthetic/*``. Endpoints are clinic-scoped via
``get_clinic_context``; patient_id is validated against the clinic on
every write. Read endpoints filter by clinic_id (multi-tenancy).
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import (
    ClinicContext,
    get_clinic_context,
    require_permission,
)
from app.core.schemas import ApiResponse, PaginatedApiResponse
from app.database import get_db

from .schemas import (
    ConsultationNoteCreate,
    ConsultationNoteResponse,
    ConsultationNoteUpdate,
    PhotoJourneyCreate,
    PhotoJourneyResponse,
    PhotoJourneyUpdate,
    ProductRecommendationCreate,
    ProductRecommendationResponse,
    ProductRecommendationUpdate,
    TreatmentHistoryCreate,
    TreatmentHistoryResponse,
    TreatmentHistoryUpdate,
)
from .service import AestheticService

router = APIRouter(prefix="/aesthetic", tags=["aesthetic"])


# --- PhotoJourney ---------------------------------------------------------


@router.get(
    "/photos",
    response_model=PaginatedApiResponse[PhotoJourneyResponse],
)
async def list_photos(
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.read"))],
    patient_id: UUID | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedApiResponse[PhotoJourneyResponse]:
    items, total = await AestheticService.list_photos(
        db, ctx.clinic_id, patient_id=patient_id, page=page, page_size=page_size
    )
    return PaginatedApiResponse(
        data=[PhotoJourneyResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/photos/{photo_id}",
    response_model=ApiResponse[PhotoJourneyResponse],
)
async def get_photo(
    photo_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.read"))],
) -> ApiResponse[PhotoJourneyResponse]:
    photo = await AestheticService.get_photo(db, ctx.clinic_id, photo_id)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return ApiResponse(data=PhotoJourneyResponse.model_validate(photo))


@router.post(
    "/photos",
    response_model=ApiResponse[PhotoJourneyResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_photo(
    payload: PhotoJourneyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.write"))],
) -> ApiResponse[PhotoJourneyResponse]:
    photo = await AestheticService.create_photo(db, ctx.clinic_id, payload.model_dump())
    await db.commit()
    await db.refresh(photo)
    return ApiResponse(data=PhotoJourneyResponse.model_validate(photo))


@router.patch(
    "/photos/{photo_id}",
    response_model=ApiResponse[PhotoJourneyResponse],
)
async def update_photo(
    photo_id: UUID,
    payload: PhotoJourneyUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.write"))],
) -> ApiResponse[PhotoJourneyResponse]:
    photo = await AestheticService.get_photo(db, ctx.clinic_id, photo_id)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    photo = await AestheticService.update_photo(db, photo, payload.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(photo)
    return ApiResponse(data=PhotoJourneyResponse.model_validate(photo))


@router.delete(
    "/photos/{photo_id}",
    response_model=ApiResponse[dict],
)
async def delete_photo(
    photo_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.write"))],
) -> ApiResponse[dict]:
    photo = await AestheticService.get_photo(db, ctx.clinic_id, photo_id)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    await AestheticService.delete_photo(db, photo)
    await db.commit()
    return ApiResponse(data={"deleted": True})


# --- ConsultationNote -----------------------------------------------------


@router.get(
    "/consultations",
    response_model=PaginatedApiResponse[ConsultationNoteResponse],
)
async def list_consultations(
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.read"))],
    patient_id: UUID | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedApiResponse[ConsultationNoteResponse]:
    items, total = await AestheticService.list_consultations(
        db, ctx.clinic_id, patient_id=patient_id, page=page, page_size=page_size
    )
    return PaginatedApiResponse(
        data=[ConsultationNoteResponse.model_validate(n) for n in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/consultations/{note_id}",
    response_model=ApiResponse[ConsultationNoteResponse],
)
async def get_consultation(
    note_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.read"))],
) -> ApiResponse[ConsultationNoteResponse]:
    note = await AestheticService.get_consultation(db, ctx.clinic_id, note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation note not found")
    return ApiResponse(data=ConsultationNoteResponse.model_validate(note))


@router.post(
    "/consultations",
    response_model=ApiResponse[ConsultationNoteResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_consultation(
    payload: ConsultationNoteCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.write"))],
) -> ApiResponse[ConsultationNoteResponse]:
    note = await AestheticService.create_consultation(
        db, ctx.clinic_id, ctx.user_id, payload.model_dump()
    )
    await db.commit()
    await db.refresh(note)
    return ApiResponse(data=ConsultationNoteResponse.model_validate(note))


@router.patch(
    "/consultations/{note_id}",
    response_model=ApiResponse[ConsultationNoteResponse],
)
async def update_consultation(
    note_id: UUID,
    payload: ConsultationNoteUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.write"))],
) -> ApiResponse[ConsultationNoteResponse]:
    note = await AestheticService.get_consultation(db, ctx.clinic_id, note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation note not found")
    note = await AestheticService.update_consultation(db, note, payload.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(note)
    return ApiResponse(data=ConsultationNoteResponse.model_validate(note))


@router.delete(
    "/consultations/{note_id}",
    response_model=ApiResponse[dict],
)
async def delete_consultation(
    note_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.write"))],
) -> ApiResponse[dict]:
    note = await AestheticService.get_consultation(db, ctx.clinic_id, note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation note not found")
    await AestheticService.delete_consultation(db, note)
    await db.commit()
    return ApiResponse(data={"deleted": True})


# --- TreatmentHistory -----------------------------------------------------


@router.get(
    "/treatments",
    response_model=PaginatedApiResponse[TreatmentHistoryResponse],
)
async def list_treatments(
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.read"))],
    patient_id: UUID | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedApiResponse[TreatmentHistoryResponse]:
    items, total = await AestheticService.list_treatments(
        db, ctx.clinic_id, patient_id=patient_id, page=page, page_size=page_size
    )
    return PaginatedApiResponse(
        data=[TreatmentHistoryResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/treatments/{treatment_id}",
    response_model=ApiResponse[TreatmentHistoryResponse],
)
async def get_treatment(
    treatment_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.read"))],
) -> ApiResponse[TreatmentHistoryResponse]:
    record = await AestheticService.get_treatment(db, ctx.clinic_id, treatment_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment not found")
    return ApiResponse(data=TreatmentHistoryResponse.model_validate(record))


@router.post(
    "/treatments",
    response_model=ApiResponse[TreatmentHistoryResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_treatment(
    payload: TreatmentHistoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.write"))],
) -> ApiResponse[TreatmentHistoryResponse]:
    record = await AestheticService.create_treatment(
        db, ctx.clinic_id, ctx.user_id, payload.model_dump()
    )
    await db.commit()
    await db.refresh(record)
    return ApiResponse(data=TreatmentHistoryResponse.model_validate(record))


@router.patch(
    "/treatments/{treatment_id}",
    response_model=ApiResponse[TreatmentHistoryResponse],
)
async def update_treatment(
    treatment_id: UUID,
    payload: TreatmentHistoryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.write"))],
) -> ApiResponse[TreatmentHistoryResponse]:
    record = await AestheticService.get_treatment(db, ctx.clinic_id, treatment_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment not found")
    record = await AestheticService.update_treatment(db, record, payload.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(record)
    return ApiResponse(data=TreatmentHistoryResponse.model_validate(record))


@router.delete(
    "/treatments/{treatment_id}",
    response_model=ApiResponse[dict],
)
async def delete_treatment(
    treatment_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.write"))],
) -> ApiResponse[dict]:
    record = await AestheticService.get_treatment(db, ctx.clinic_id, treatment_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment not found")
    await AestheticService.delete_treatment(db, record)
    await db.commit()
    return ApiResponse(data={"deleted": True})


# --- ProductRecommendation ------------------------------------------------


@router.get(
    "/recommendations",
    response_model=PaginatedApiResponse[ProductRecommendationResponse],
)
async def list_recommendations(
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.read"))],
    patient_id: UUID | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedApiResponse[ProductRecommendationResponse]:
    items, total = await AestheticService.list_recommendations(
        db, ctx.clinic_id, patient_id=patient_id, page=page, page_size=page_size
    )
    return PaginatedApiResponse(
        data=[ProductRecommendationResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/recommendations/{rec_id}",
    response_model=ApiResponse[ProductRecommendationResponse],
)
async def get_recommendation(
    rec_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.read"))],
) -> ApiResponse[ProductRecommendationResponse]:
    rec = await AestheticService.get_recommendation(db, ctx.clinic_id, rec_id)
    if rec is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    return ApiResponse(data=ProductRecommendationResponse.model_validate(rec))


@router.post(
    "/recommendations",
    response_model=ApiResponse[ProductRecommendationResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_recommendation(
    payload: ProductRecommendationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.write"))],
) -> ApiResponse[ProductRecommendationResponse]:
    rec = await AestheticService.create_recommendation(
        db, ctx.clinic_id, ctx.user_id, payload.model_dump()
    )
    await db.commit()
    await db.refresh(rec)
    return ApiResponse(data=ProductRecommendationResponse.model_validate(rec))


@router.patch(
    "/recommendations/{rec_id}",
    response_model=ApiResponse[ProductRecommendationResponse],
)
async def update_recommendation(
    rec_id: UUID,
    payload: ProductRecommendationUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.write"))],
) -> ApiResponse[ProductRecommendationResponse]:
    rec = await AestheticService.get_recommendation(db, ctx.clinic_id, rec_id)
    if rec is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    rec = await AestheticService.update_recommendation(db, rec, payload.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(rec)
    return ApiResponse(data=ProductRecommendationResponse.model_validate(rec))


@router.delete(
    "/recommendations/{rec_id}",
    response_model=ApiResponse[dict],
)
async def delete_recommendation(
    rec_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic.write"))],
) -> ApiResponse[dict]:
    rec = await AestheticService.get_recommendation(db, ctx.clinic_id, rec_id)
    if rec is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    await AestheticService.delete_recommendation(db, rec)
    await db.commit()
    return ApiResponse(data={"deleted": True})