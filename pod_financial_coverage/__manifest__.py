# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Financial Coverage",
    "summary": "Add Coverage concept",
    "version": "15.0.1.0.0",
    "author": "CreuBlanca, ForgeFlow, Odoo Community Association (OCA)",
    "category": "Podiatry",
    "website": "https://github.com/tegin/pod-fhir",
    "license": "LGPL-3",
    "depends": ["pod_base"],
    "data": [
        "security/ir.model.access.csv",
        "data/pod_payor_sequence.xml",
        "data/pod_coverage_sequence.xml",
        "views/pod_patient_views.xml",
        "views/res_partner_views.xml",
        "views/pod_coverage_template_view.xml",
        "views/pod_coverage_view.xml",
        "views/pod_menu.xml",
    ],
    "demo": ["demo/pod_coverage.xml"],
    "installable": True,
    "auto_install": False,
}
