

{
    "name": "Podiatry Clinical Request Group",
    "summary": "Podiatry request group",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": ["podiatry_clinical", "podiatry_workflow"],
    "data": [
        "data/ir_sequence_data.xml",
        "data/podiatry_workflow.xml",
        "security/podiatry_security.xml",
        "security/ir.model.access.csv",
        "views/podiatry_request_view.xml",
        "views/podiatry_request_group_view.xml",
    ],
    "demo": ["demo/podiatry_demo.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
