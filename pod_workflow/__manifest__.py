# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Workflow",
    "summary": "Podiatry workflow base",
    "version": "15.0.1.0.1",
    "author": "CreuBlanca, ForgeFlow, Odoo Community Association (OCA)",
    "category": "Podiatry",
    "website": "https://github.com/tegin/pod-fhir",
    "license": "LGPL-3",
    "depends": ["pod_administration_practitioner", "product"],
    "data": [
        "data/ir_sequence.xml",
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "wizard/pod_add_plan_definition_views.xml",
        "views/workflow_activity_definition.xml",
        "views/workflow_plan_definition.xml",
        "views/workflow_plan_definition_action.xml",
        "views/res_config_settings_views.xml",
        "views/pod_patient.xml",
        "views/pod_request_view.xml",
        "views/pod_event_view.xml",
    ],
    "demo": ["demo/pod_demo.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
