

{
    "name": "Podiatry Clinical Request Group",
    "summary": "Podiatry request group",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": ["pod_workflow"],
    "data": [
        "data/ir_sequence_data.xml",
        "security/ir.model.access.csv",
        "views/pod_request_view.xml",
        "views/pod_request_group_view.xml",
    ],
    "demo": ["demo/pod_demo.xml"],
    "installable": True,
}
