

{
    "name": "Podiatry Clinical Procedure",
    "summary": "Podiatry Procedures and Procedure requests",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": [
        "pod_workflow",
        "pod_base",
    ],
    "data": [
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "wizard/pod_procedure_request_make_procedure_view.xml",
        "views/pod_request_views.xml",
        "views/pod_procedure_view.xml",
        "views/pod_procedure_request_view.xml",
    ],
    "demo": ["demo/pod_demo.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
