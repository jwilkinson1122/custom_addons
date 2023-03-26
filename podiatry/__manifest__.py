# See LICENSE file for full copyright and licensing details.

{
    "name": "Podiatry Management",
    "version": "15.0.1.0.0",
    "author": "Odoo Community Association (OCA), Serpent Consulting \
               Services Pvt. Ltd., OpenERP SA",
    "category": "Podiatry Management",
    "website": "https://github.com/OCA/vertical-podiatry",
    "depends": ["sale_stock", "account"],
    "license": "LGPL-3",
    "summary": "Podiatry Management to Manage Folio and Podiatry Configuration",
    "demo": ["demo/podiatry_data.xml"],
    "data": [
        "security/podiatry_security.xml",
        "security/ir.model.access.csv",
        "data/podiatry_sequence.xml",
        "report/report_view.xml",
        "report/podiatry_folio_report_template.xml",
        "views/podiatry_folio.xml",
        "views/podiatry_room.xml",
        "views/podiatry_room_amenities.xml",
        "views/podiatry_room_type.xml",
        "views/podiatry_service_type.xml",
        "views/podiatry_services.xml",
        "views/product_product.xml",
        "views/res_company.xml",
        "views/actions.xml",
        "views/menus.xml",
        "wizard/podiatry_wizard.xml",
    ],
    "assets": {
        "web.assets_backend": ["podiatry/static/src/css/room_kanban.css"],
    },
    "external_dependencies": {"python": ["python-dateutil"]},
    "images": ["static/description/Podiatry.png"],
    "application": True,
}
