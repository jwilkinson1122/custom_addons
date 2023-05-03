# See LICENSE file for full copyright and licensing details.

{
    "name": "Pod ERP",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Account Management",
    "website": "https://nwpodiatric.com",
    "depends": ["sale_stock", "account"],
    "license": "LGPL-3",
    "summary": "Account Management to Manage Prescription and Account Configuration",
    "demo": ["demo/account_data.xml"],
    "data": [
        "security/account_security.xml",
        "security/ir.model.access.csv",
        "data/account_sequence.xml",
        "report/report_view.xml",
        "report/account_prescription_report_template.xml",
        "views/account_prescription.xml",
        "views/account_device.xml",
        "views/account_device_customizations.xml",
        "views/account_device_type.xml",
        "views/account_service_type.xml",
        "views/account_services.xml",
        "views/product_product.xml",
        "views/res_company.xml",
        "views/actions.xml",
        "views/menus.xml",
        "wizard/account_wizard.xml",
    ],
    "assets": {
        "web.assets_backend": ["pod_manager/static/src/css/device_kanban.css"],
    },
    "external_dependencies": {"python": ["python-dateutil"]},
    "images": ["static/description/icon.png"],
    "application": True,
}
