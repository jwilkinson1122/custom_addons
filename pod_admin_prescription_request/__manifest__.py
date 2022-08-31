

{
    "name": "Podiatry Prescription Request",
    "summary": "Podiatry device request and administration",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": [
        "podiatry_workflow",
        "podiatry_clinical",
        "podiatry_device",
        "podiatry_administration_location_stock",
    ],
    "data": [
        "security/podiatry_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/stock_location.xml",
        "data/podiatry_workflow.xml",
        "views/podiatry_request_views.xml",
        "views/podiatry_device_administration_view.xml",
        "views/podiatry_device_request.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
