# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Device Request",
    "summary": "Podiatry device request and administration",
    "version": "15.0.1.0.0",
    "author": "CreuBlanca, ForgeFlow, Odoo Community Association (OCA)",
    "category": "Podiatry",
    "website": "https://github.com/tegin/pod-fhir",
    "license": "LGPL-3",
    "depends": [
        "pod_workflow",
        "pod_device",
        "pod_administration_location_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/stock_location.xml",
        "views/pod_request_views.xml",
        "views/pod_device_administration_view.xml",
        "views/pod_device_request.xml",
    ],
    "installable": True,
}
