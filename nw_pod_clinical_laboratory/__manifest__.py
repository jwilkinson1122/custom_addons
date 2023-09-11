{
    "name": "Podiatry Clinical Laboratory",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "depends": ["nw_pod_prescription"],
    "data": [
        "security/ir.model.access.csv",
        "views/pod_coverage_template_views.xml",
        "views/pod_laboratory_event_view.xml",
        "views/pod_laboratory_request_view.xml",
        "views/workflow_activity_definition_views.xml",
        "views/pod_laboratory_service_view.xml",
    ],
    "website": "https://nwpodiatric.com",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
