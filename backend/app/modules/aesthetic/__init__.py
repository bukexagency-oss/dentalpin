"""Aesthetic module — esthetic clinic workflow.

PhotoJourney (before/after), ConsultationNote, TreatmentHistory and
ProductRecommendation for the Otomedis esthetic clinic fork. Every
entity is scoped by clinic_id (multi-tenant) and patient_id.

This module owns the ``aesthetic.*`` permission namespace.
"""

from fastapi import APIRouter

from app.core.plugins import BaseModule

from .models import (
    ConsultationNote,
    PhotoJourney,
    ProductRecommendation,
    TreatmentHistory,
)
from .router import router


class AestheticModule(BaseModule):
    """Esthetic clinic workflow: photo journey, consultations, treatments, product recs."""

    manifest = {
        "name": "aesthetic",
        "version": "0.1.0",
        "summary": "Esthetic clinic workflow: photo journey, consultation notes, treatment history, product recommendations.",
        "author": "Otomedis Core Team",
        "license": "BSL-1.1",
        "category": "official",
        "depends": ["patients"],
        "installable": True,
        "auto_install": True,
        "removable": False,
        "role_permissions": {
            "admin": ["*"],
            "dentist": ["*"],
            "hygienist": ["read"],
            "assistant": ["read", "write"],
            "receptionist": ["read"],
        },
        "frontend": {
            "layer_path": "frontend",
            "navigation": [
                {
                    "label": "nav.aesthetic",
                    "icon": "i-lucide-sparkles",
                    "to": "/aesthetic",
                    "permission": "aesthetic.read",
                    "order": 15,
                },
            ],
        },
    }

    def get_models(self) -> list:
        return [
            PhotoJourney,
            ConsultationNote,
            TreatmentHistory,
            ProductRecommendation,
        ]

    def get_router(self) -> APIRouter:
        return router

    def get_permissions(self) -> list[str]:
        return ["read", "write"]
