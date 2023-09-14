# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Care plan",
    "summary": "Podiatry care plan",
    "version": "15.0.1.0.0",
    "author": "CreuBlanca, ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/pod-fhir",
    "category": "Podiatry",
    "license": "LGPL-3",
    "depends": ["pod_workflow"],
    "data": [
        "data/ir_sequence_data.xml",
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "wizard/pod_careplan_add_plan_definition_views.xml",
        "views/pod_request_views.xml",
        "views/pod_careplan_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
