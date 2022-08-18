
{
    "name": "Podiatry Care plan",
    "summary": "Podiatry care plan",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "category": "Medical",
    "license": "LGPL-3",
    "depends": ["pod_clinical", "pod_workflow"],
    "data": [
        "data/ir_sequence_data.xml",
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "wizard/pod_careplan_add_plan_definition_views.xml",
        "views/pod_request_views.xml",
        "views/pod_careplan_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
