

{
    "name": "Podiatry Clinical Laboratory",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "depends": ["nwp_pod_device"],
    "data": [
        "security/ir.model.access.csv",
        "views/pod_coverage_template_views.xml",
        "views/pod_laboratory_event_view.xml",
        "views/pod_laboratory_request_view.xml",
        "views/workflow_activity_definition_views.xml",
        "views/pod_laboratory_service_view.xml",
    ],
    "website": "https://github.com/tegin/nwp-pod",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
