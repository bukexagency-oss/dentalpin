"""HTTP surface for skin_analysis.

Minimal Fase 2a: a stub router with a health/echo endpoint and a
Fitzpatrick scale reference list. Full assessment CRUD lands in a later
phase. Mounted under ``/api/v1/skin_analysis/*``.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import (
    ClinicContext,
    get_clinic_context,
    require_permission,
)
from app.core.schemas import ApiResponse
from app.database import get_db

router = APIRouter(prefix="/skin_analysis", tags=["skin_analysis"])

FITZPATRICK_TYPES = [
    {"type": "I", "description": "Very fair, always burns, never tans"},
    {"type": "II", "description": "Fair, usually burns, tans minimally"},
    {"type": "III", "description": "Light-medium, sometimes burns, tans evenly"},
    {"type": "IV", "description": "Medium, rarely burns, tans easily"},
    {"type": "V", "description": "Dark brown, very rarely burns, tans very easily"},
    {"type": "VI", "description": "Deeply pigmented, never burns"},
]


@router.get("/fitzpatrick", response_model=ApiResponse[list[dict]])
async def list_fitzpatrick(
    db: Annotated[AsyncSession, Depends(get_db)],
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("skin_analysis.read"))],
) -> ApiResponse[list[dict]]:
    return ApiResponse(data=FITZPATRICK_TYPES)
