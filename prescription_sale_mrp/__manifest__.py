{
    "name": "Return Product Authorization Management",
    "summary": "Allow doing Prescription from MRP kits",
    "version": "17.0.0.0.0",
    "category": "Prescription",
    "website": "https://nwpodiatric.com",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": [
        "prescription_sale", 
        "mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_portal_template.xml",
        "views/prescription_views.xml",
        "views/report_prescription.xml",
        "wizard/sale_order_prescription_wizard_views.xml",
    ],
}
