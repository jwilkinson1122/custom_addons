{
    "name": "Podiatry Prescription Request",
    "summary": "Podiatry prescription request and administration",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": [
        "pod_workflow",
        "pod_prescription",
        "pod_administration_location_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/stock_location.xml",
        "views/pod_request_views.xml",
        "views/pod_prescription_administration_view.xml",
        "views/pod_prescription_request.xml",
    ],
    "installable": True,
}
