

{
    "name": "Podiatry Workflow",
    "summary": "Podiatry workflow base",
    "version": "15.0.1.0.1",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": ["pod_base", "product"],
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
