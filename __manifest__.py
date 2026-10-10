# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MBA - Mejoras de Acuerdos y Contratos",
    "version": "19.0.1.0.0",
    "category": "Contract",
    "summary": "Auto-población de cláusulas desde plantillas y mejoras de UX en Acuerdos",
    "author": "MBA Consultings",
    "website": "https://mbaconsultings.com",
    "license": "AGPL-3",
    "depends": [
        "agreement_legal",
        "agreement_sale",
        "agreement_project",
    ],
    "data": [
        "views/agreement_views.xml",
        "reports/agreement_persona_natural_report.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
