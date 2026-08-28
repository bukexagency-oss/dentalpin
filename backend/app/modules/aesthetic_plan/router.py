"""Treatment plan module API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import ClinicContext, get_clinic_context, require_permission
from app.core.schemas import ApiResponse, PaginatedApiResponse
from app.database import get_db

from .schemas import (
    ClosePlanRequest,
    CompleteItemRequest,
    CompleteSessionRequest,
    ContactLogRequest,
    GenerateBudgetResponse,
    LinkBudgetRequest,
    PipelineRow,
    AestheticPlanItemCreate,
    AestheticPlanItemResponse,
    AestheticPlanItemUpdate,
    ReorderItemsRequest,
    SessionInput,
    AestheticPlanCreate,
    AestheticPlanDetailResponse,
    AestheticPlanResponse,
    AestheticPlanStatusUpdate,
    AestheticPlanUpdate,
    UpdateSessionRequest,
)
from .service import PlanLockedError, AestheticPlanService

router = APIRouter()


# -----------------------------------------------------------------------------
# Bandeja de planes (pipeline view) — declared FIRST so the literal
# ``/aesthetic-plans/pipeline`` path matches before any ``/{plan_id}``
# pattern below it. FastAPI resolves routes in registration order.
# -----------------------------------------------------------------------------


PIPELINE_TABS = {
    "por_presupuestar",
    "esperando_paciente",
    "sin_cita",
    "sin_proxima_cita",
    "cerrados",
}


@router.get(
    "/aesthetic-plans/pipeline",
    response_model=PaginatedApiResponse[PipelineRow],
)
async def list_pipeline(
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.read"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    tab: str = Query(..., description="One of: " + ", ".join(sorted(PIPELINE_TABS))),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    doctor_id: UUID | None = Query(default=None),
    q: str | None = Query(default=None, description="Free-text search"),
) -> PaginatedApiResponse[PipelineRow]:
    """Bandeja de planes (cross-module pipeline view).

    The endpoint joins ``aesthetic_plans``, ``budgets`` and
    ``appointments`` directly via SQL because all three are declared in
    treatment_plan's manifest.depends. Filtering happens in SQL by tab.
    """
    if tab not in PIPELINE_TABS:
        raise HTTPException(status_code=400, detail=f"Unknown tab '{tab}'")

    rows, total = await AestheticPlanService.list_pipeline(
        db,
        clinic_id=ctx.clinic_id,
        tab=tab,
        page=page,
        page_size=page_size,
        doctor_id=doctor_id,
        search=q,
    )
    return PaginatedApiResponse(
        data=rows,
        total=total,
        page=page,
        page_size=page_size,
    )


# -----------------------------------------------------------------------------
# Treatment Plans CRUD
# -----------------------------------------------------------------------------


@router.get("/aesthetic-plans", response_model=PaginatedApiResponse[AestheticPlanResponse])
async def list_aesthetic_plans(
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.read"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    patient_id: UUID | None = None,
    status: list[str] | None = Query(default=None),
) -> PaginatedApiResponse[AestheticPlanResponse]:
    """List treatment plans with pagination and filters."""
    plans, total = await AestheticPlanService.list(
        db, ctx.clinic_id, page, page_size, patient_id=patient_id, status=status
    )
    # Compute counts and totals from loaded items
    for p in plans:
        items = p.items or []
        p.item_count = len(items)
        p.completed_count = sum(1 for i in items if i.status == "completed")
        p.total = sum(
            float(i.treatment.price_snapshot) if i.treatment and i.treatment.price_snapshot else 0
            for i in items
        )
    return PaginatedApiResponse(
        data=[AestheticPlanResponse.model_validate(p) for p in plans],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/aesthetic-plans/patient/{patient_id}",
    response_model=PaginatedApiResponse[AestheticPlanResponse],
)
async def list_patient_plans(
    patient_id: UUID,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.read"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedApiResponse[AestheticPlanResponse]:
    """List treatment plans for a specific patient."""
    plans, total = await AestheticPlanService.list(
        db, ctx.clinic_id, page, page_size, patient_id=patient_id
    )
    # Compute counts and totals from loaded items
    for p in plans:
        items = p.items or []
        p.item_count = len(items)
        p.completed_count = sum(1 for i in items if i.status == "completed")
        p.total = sum(
            float(i.treatment.price_snapshot) if i.treatment and i.treatment.price_snapshot else 0
            for i in items
        )
    return PaginatedApiResponse(
        data=[AestheticPlanResponse.model_validate(p) for p in plans],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/aesthetic-plans/{plan_id}",
    response_model=ApiResponse[AestheticPlanDetailResponse],
)
async def get_treatment_plan(
    plan_id: UUID,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.read"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanDetailResponse]:
    """Get a treatment plan with full details."""
    plan = await AestheticPlanService.get(db, ctx.clinic_id, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Treatment plan not found")
    return ApiResponse(data=AestheticPlanDetailResponse.model_validate(plan))


@router.post(
    "/aesthetic-plans",
    response_model=ApiResponse[AestheticPlanResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_treatment_plan(
    data: AestheticPlanCreate,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanResponse]:
    """Create a new treatment plan."""
    try:
        plan = await AestheticPlanService.create(db, ctx.clinic_id, ctx.user_id, data.model_dump())
        return ApiResponse(data=AestheticPlanResponse.model_validate(plan))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/aesthetic-plans/{plan_id}",
    response_model=ApiResponse[AestheticPlanResponse],
)
async def update_treatment_plan(
    plan_id: UUID,
    data: AestheticPlanUpdate,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanResponse]:
    """Update a treatment plan."""
    try:
        plan = await AestheticPlanService.update(
            db, ctx.clinic_id, plan_id, data.model_dump(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not plan:
        raise HTTPException(status_code=404, detail="Treatment plan not found")
    return ApiResponse(data=AestheticPlanResponse.model_validate(plan))


@router.patch(
    "/aesthetic-plans/{plan_id}/status",
    response_model=ApiResponse[AestheticPlanResponse],
)
async def update_plan_status(
    plan_id: UUID,
    data: AestheticPlanStatusUpdate,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanResponse]:
    """Change treatment plan status."""
    try:
        plan = await AestheticPlanService.update_status(
            db, ctx.clinic_id, plan_id, data.status, ctx.user_id
        )
        if not plan:
            raise HTTPException(status_code=404, detail="Treatment plan not found")
        return ApiResponse(data=AestheticPlanResponse.model_validate(plan))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------------------------------------------------
# Workflow transitions (confirm / reopen / close / reactivate)
# -----------------------------------------------------------------------------


@router.post(
    "/aesthetic-plans/{plan_id}/confirm",
    response_model=ApiResponse[AestheticPlanResponse],
)
async def confirm_treatment_plan(
    plan_id: UUID,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.confirm"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanResponse]:
    """Doctor confirms the plan (``draft`` → ``pending``).

    Auto-creates the draft budget so reception can review and send.
    """
    try:
        plan = await AestheticPlanService.confirm(db, ctx.clinic_id, plan_id, ctx.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ApiResponse(data=AestheticPlanResponse.model_validate(plan))


@router.post(
    "/aesthetic-plans/{plan_id}/reopen",
    response_model=ApiResponse[AestheticPlanResponse],
)
async def reopen_treatment_plan(
    plan_id: UUID,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanResponse]:
    """Reopen a confirmed plan back to ``draft`` and cancel its budget."""
    try:
        plan = await AestheticPlanService.reopen(db, ctx.clinic_id, plan_id, ctx.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ApiResponse(data=AestheticPlanResponse.model_validate(plan))


@router.post(
    "/aesthetic-plans/{plan_id}/close",
    response_model=ApiResponse[AestheticPlanResponse],
)
async def close_treatment_plan(
    plan_id: UUID,
    data: ClosePlanRequest,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.close"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanResponse]:
    """Move the plan to terminal ``closed`` state with a reason."""
    try:
        plan = await AestheticPlanService.close(
            db,
            ctx.clinic_id,
            plan_id,
            ctx.user_id,
            closure_reason=data.closure_reason,
            closure_note=data.closure_note,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ApiResponse(data=AestheticPlanResponse.model_validate(plan))


@router.post(
    "/aesthetic-plans/{plan_id}/reactivate",
    response_model=ApiResponse[AestheticPlanResponse],
)
async def reactivate_treatment_plan(
    plan_id: UUID,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.reactivate"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanResponse]:
    """Revive a closed plan back to ``draft`` for a fresh cycle."""
    try:
        plan = await AestheticPlanService.reactivate(db, ctx.clinic_id, plan_id, ctx.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ApiResponse(data=AestheticPlanResponse.model_validate(plan))


@router.post(
    "/aesthetic-plans/{plan_id}/contact-log",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def log_plan_contact(
    plan_id: UUID,
    data: ContactLogRequest,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Record a non-state-changing contact with the patient.

    The bandeja sorts ``Esperando paciente`` by ``last_contact`` so
    reception can prioritise calls. We persist the touchpoint via the
    plan's ``internal_notes`` for now (one-line append). A dedicated
    contact-log table is on the v2 backlog.
    """
    from datetime import UTC, datetime

    plan = await AestheticPlanService.get(db, ctx.clinic_id, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Treatment plan not found")
    timestamp = datetime.now(UTC).isoformat()
    line = f"[{timestamp}] {data.channel} by {ctx.user_id}"
    if data.note:
        line += f" — {data.note.strip()}"
    plan.internal_notes = f"{plan.internal_notes}\n{line}".strip() if plan.internal_notes else line
    await db.flush()


@router.delete("/aesthetic-plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_treatment_plan(
    plan_id: UUID,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Soft delete (archive) a treatment plan."""
    deleted = await AestheticPlanService.delete(db, ctx.clinic_id, plan_id, ctx.user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Treatment plan not found")


# -----------------------------------------------------------------------------
# Plan Items
# -----------------------------------------------------------------------------


@router.post(
    "/aesthetic-plans/{plan_id}/items",
    response_model=ApiResponse[AestheticPlanItemResponse],
    status_code=status.HTTP_201_CREATED,
)
async def add_plan_item(
    plan_id: UUID,
    data: AestheticPlanItemCreate,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanItemResponse]:
    """Add a treatment item to the plan."""
    try:
        item = await AestheticPlanService.add_item(db, ctx.clinic_id, plan_id, data.model_dump())
        return ApiResponse(data=AestheticPlanItemResponse.model_validate(item))
    except PlanLockedError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/aesthetic-plans/{plan_id}/items/{item_id}",
    response_model=ApiResponse[AestheticPlanItemResponse],
)
async def update_plan_item(
    plan_id: UUID,
    item_id: UUID,
    data: AestheticPlanItemUpdate,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanItemResponse]:
    """Update a planned treatment item."""
    try:
        item = await AestheticPlanService.update_item(
            db, ctx.clinic_id, plan_id, item_id, data.model_dump(exclude_unset=True)
        )
    except PlanLockedError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not item:
        raise HTTPException(status_code=404, detail="Treatment item not found")
    return ApiResponse(data=AestheticPlanItemResponse.model_validate(item))


@router.delete(
    "/aesthetic-plans/{plan_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_plan_item(
    plan_id: UUID,
    item_id: UUID,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Remove an item from the plan."""
    try:
        removed = await AestheticPlanService.remove_item(
            db, ctx.clinic_id, plan_id, item_id, ctx.user_id
        )
    except PlanLockedError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if not removed:
        raise HTTPException(status_code=404, detail="Treatment item not found")


@router.patch(
    "/aesthetic-plans/{plan_id}/items/reorder",
    response_model=ApiResponse[AestheticPlanDetailResponse],
)
async def reorder_plan_items(
    plan_id: UUID,
    data: ReorderItemsRequest,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanDetailResponse]:
    """Reorder all items of a plan in a single atomic call.

    `item_ids` MUST cover exactly the plan's current items. Returns the full plan
    with items in the new order so the caller doesn't need a second round-trip.
    """
    try:
        items = await AestheticPlanService.reorder_items(db, ctx.clinic_id, plan_id, data.item_ids)
    except PlanLockedError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if items is None:
        raise HTTPException(status_code=404, detail="Treatment plan not found")

    plan = await AestheticPlanService.get(db, ctx.clinic_id, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Treatment plan not found")
    return ApiResponse(data=AestheticPlanDetailResponse.model_validate(plan))


@router.patch(
    "/aesthetic-plans/{plan_id}/items/{item_id}/complete",
    response_model=ApiResponse[AestheticPlanItemResponse],
)
async def complete_plan_item(
    plan_id: UUID,
    item_id: UUID,
    data: CompleteItemRequest,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanItemResponse]:
    """Mark a treatment item as completed."""
    try:
        item = await AestheticPlanService.complete_item(
            db,
            ctx.clinic_id,
            plan_id,
            item_id,
            ctx.user_id,
            data.completed_without_appointment,
            data.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not item:
        raise HTTPException(status_code=404, detail="Treatment item not found")
    return ApiResponse(data=AestheticPlanItemResponse.model_validate(item))


# -----------------------------------------------------------------------------
# Plan item sessions (multi-session billing)
# -----------------------------------------------------------------------------


def _item_response_or_404(item) -> ApiResponse[AestheticPlanItemResponse]:
    if not item:
        raise HTTPException(status_code=404, detail="Treatment item not found")
    return ApiResponse(data=AestheticPlanItemResponse.model_validate(item))


@router.patch(
    "/aesthetic-plans/{plan_id}/items/{item_id}/sessions/{session_id}/complete",
    response_model=ApiResponse[AestheticPlanItemResponse],
)
async def complete_item_session(
    plan_id: UUID,
    item_id: UUID,
    session_id: UUID,
    data: CompleteSessionRequest,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanItemResponse]:
    """Mark one session of a plan item as completed."""
    try:
        item = await AestheticPlanService.complete_session(
            db,
            ctx.clinic_id,
            plan_id,
            item_id,
            session_id,
            ctx.user_id,
            data.completed_without_appointment,
            data.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _item_response_or_404(item)


@router.patch(
    "/aesthetic-plans/{plan_id}/items/{item_id}/sessions/{session_id}/cancel",
    response_model=ApiResponse[AestheticPlanItemResponse],
)
async def cancel_item_session(
    plan_id: UUID,
    item_id: UUID,
    session_id: UUID,
    data: CompleteSessionRequest,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanItemResponse]:
    """Mark a session as cancelled (no earned entry will be generated)."""
    try:
        item = await AestheticPlanService.cancel_session(
            db, ctx.clinic_id, plan_id, item_id, session_id, ctx.user_id, data.notes
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _item_response_or_404(item)


@router.put(
    "/aesthetic-plans/{plan_id}/items/{item_id}/sessions/{session_id}",
    response_model=ApiResponse[AestheticPlanItemResponse],
)
async def update_item_session(
    plan_id: UUID,
    item_id: UUID,
    session_id: UUID,
    data: UpdateSessionRequest,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanItemResponse]:
    """Edit label / amount / notes on a pending session."""
    try:
        item = await AestheticPlanService.update_session(
            db,
            ctx.clinic_id,
            plan_id,
            item_id,
            session_id,
            data.model_dump(exclude_unset=True),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _item_response_or_404(item)


@router.post(
    "/aesthetic-plans/{plan_id}/items/{item_id}/sessions",
    response_model=ApiResponse[AestheticPlanItemResponse],
    status_code=status.HTTP_201_CREATED,
)
async def add_item_session(
    plan_id: UUID,
    item_id: UUID,
    data: SessionInput,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanItemResponse]:
    """Append a new session to a plan item (manual; outside catalog template)."""
    try:
        item = await AestheticPlanService.add_session_manual(
            db,
            ctx.clinic_id,
            plan_id,
            item_id,
            data.model_dump(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _item_response_or_404(item)


@router.delete(
    "/aesthetic-plans/{plan_id}/items/{item_id}/sessions/{session_id}",
    response_model=ApiResponse[AestheticPlanItemResponse],
)
async def delete_item_session(
    plan_id: UUID,
    item_id: UUID,
    session_id: UUID,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanItemResponse]:
    """Remove a pending session. Returns the updated item."""
    try:
        item = await AestheticPlanService.delete_session(
            db, ctx.clinic_id, plan_id, item_id, session_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _item_response_or_404(item)


# -----------------------------------------------------------------------------
# Budget Integration
# -----------------------------------------------------------------------------


@router.post(
    "/aesthetic-plans/{plan_id}/link-budget",
    response_model=ApiResponse[AestheticPlanResponse],
)
async def link_budget_to_plan(
    plan_id: UUID,
    data: LinkBudgetRequest,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[AestheticPlanResponse]:
    """Link an existing budget to the treatment plan."""
    try:
        plan = await AestheticPlanService.link_budget(db, ctx.clinic_id, plan_id, data.budget_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Treatment plan not found")
        return ApiResponse(data=AestheticPlanResponse.model_validate(plan))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/aesthetic-plans/{plan_id}/sync-budget",
    response_model=ApiResponse[dict],
)
async def sync_plan_with_budget(
    plan_id: UUID,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[dict]:
    """Request synchronization of plan items with linked budget."""
    success = await AestheticPlanService.request_budget_sync(db, ctx.clinic_id, plan_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot sync: plan not found or no budget linked",
        )
    return ApiResponse(data={"synced": True})


@router.post(
    "/aesthetic-plans/{plan_id}/generate-budget",
    response_model=ApiResponse[GenerateBudgetResponse],
    status_code=status.HTTP_201_CREATED,
)
async def generate_budget_from_plan(
    plan_id: UUID,
    ctx: Annotated[ClinicContext, Depends(get_clinic_context)],
    _: Annotated[None, Depends(require_permission("aesthetic_plan.plans.write"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[GenerateBudgetResponse]:
    """Generate a new budget from the treatment plan items."""
    from app.modules.budget.service import BudgetService

    plan = await AestheticPlanService.get(db, ctx.clinic_id, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Treatment plan not found")

    # Check if existing linked budget is cancelled - if so, allow creating new one
    if plan.budget_id:
        from app.modules.budget.models import Budget

        existing_budget = await db.get(Budget, plan.budget_id)
        if existing_budget and existing_budget.status == "cancelled":
            # Unlink cancelled budget to allow new one
            plan.budget_id = None
        else:
            raise HTTPException(status_code=400, detail="Plan already has a budget linked")

    if not plan.items:
        raise HTTPException(status_code=400, detail="Plan has no items to create budget from")

    # Collect catalog items from plan items, resolving everything from Treatment.
    budget_items = []
    for item in plan.items:
        treatment = item.treatment
        if not treatment or not treatment.catalog_item_id:
            continue
        primary_tooth = treatment.teeth[0].tooth_number if treatment.teeth else None
        primary_surfaces = treatment.teeth[0].surfaces if treatment.teeth else None
        budget_items.append(
            {
                "catalog_item_id": str(treatment.catalog_item_id),
                "quantity": 1,
                "tooth_number": primary_tooth,
                "surfaces": primary_surfaces,
                "treatment_id": str(treatment.id),
                "unit_price": treatment.price_snapshot,
            }
        )

    if not budget_items:
        raise HTTPException(
            status_code=400,
            detail="No catalog items found in plan to create budget",
        )

    # Create budget via budget service
    from datetime import date

    budget = await BudgetService.create_budget(
        db,
        ctx.clinic_id,
        ctx.user_id,
        {
            "patient_id": plan.patient_id,
            "valid_from": date.today(),
            "items": budget_items,
            "internal_notes": f"Generated from treatment plan {plan.plan_number}",
        },
    )

    # Link budget to plan
    plan.budget_id = budget.id

    return ApiResponse(
        data=GenerateBudgetResponse(
            budget_id=budget.id,
            budget_number=budget.budget_number,
        )
    )


# Media attachment endpoints moved to the ``media`` module since issue #55.
# Use ``POST /api/v1/media/attachments`` with ``owner_type='plan_item'``.
#
# Clinical-notes endpoints moved to the ``clinical_notes`` module since
# issue #60 (``/api/v1/clinical_notes/*``).
