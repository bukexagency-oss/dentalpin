"""indonesia_regulation — NPWP, PPN (VAT), and e-invoice compliance for Indonesia.

Stores per-clinic NPWP registration data and tracks e-invoice (Faktur Pajak)
submission lifecycle. The data populates invoice footer / tax line / e-invoice
status without tying billing or catalog to a single country's fiscal rules.

Manual install (``auto_install=False``). The module is suggested when the
clinic's country preset is ``ID``.
"""

from app.core.plugins import BaseModule

from .models import (
    IndonesiaRegulationSettings,
    IndonesiaRegulationEInvoiceSubmission,
)


class IndonesiaRegulationModule(BaseModule):
    manifest = {
        "name": "indonesia_regulation",
        "version": "0.1.0",
        "summary": "NPWP, PPN compliance, and e-invoice (Faktur Pajak) for Indonesia.",
        "auto_install": False,
        "removable": True,
        "suggested_for_country": "ID",
        "models": [
            IndonesiaRegulationSettings,
            IndonesiaRegulationEInvoiceSubmission,
        ],
    }