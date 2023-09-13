

{
    "name": "Podiatry Laboratory",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "depends": ["pod_workflow", "pod_base"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/pod_request_views.xml",
        "views/pod_laboratory_event_view.xml",
        "views/pod_laboratory_request_view.xml",
    ],
    "website": "https://nwpodiatric.com",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
