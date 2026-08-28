"""Skin analysis module — minimal for Fase 2a.

Skin type assessment, Fitzpatrick scale, and treatment contraindications.
Optional this phase — basic structure provided for pyproject entry point.
"""

from fastapi import APIRouter

from app.core.plugins import BaseModule

from .router import router


class SkinAnalysisModule(BaseModule):
    """Skin analysis: Fitzpatrick scale, skin type, contraindications."""

    manifest = {
        "name": "skin_analysis",
        "version": "0.1.0",
        "summary": "Skin analysis: Fitzpatrick scale, assessment, contraindications.",
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
    }

    def get_models(self) -> list:
        return []

    def get_router(self) -> APIRouter:
        return router

    def get_permissions(self) -> list[str]:
        return ["read", "write"]