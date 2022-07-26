
{
    "name": "Pod Clinical Request Group",
    "summary": "Pod request group",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Medical",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": ["pod_clinical", "pod_workflow"],
    "data": [
        "data/ir_sequence_data.xml",
        "data/pod_workflow.xml",
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "views/pod_request_view.xml",
        "views/pod_request_group_view.xml",
    ],
    "demo": ["demo/pod_demo.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
