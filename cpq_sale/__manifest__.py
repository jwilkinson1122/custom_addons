{
    "name": "CPQ Sale",
    "summary": "Glue module between CPQ and Sale",
    "author": "NWPL",
    "category": "Uncategorized",
    "version": "17.0.1.0.0",
    "depends": ["base", "web", "cpq", "sale", "sale_management", "sale_product_configurator", "mail"],
    "auto_install": ["cpq", "sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order.xml",
        "views/sale_order_line.xml",
        "views/product_template.xml",
        "views/create_product_wizard.xml",
        "views/batch_create_product_wizard.xml",
        "reports/reports.xml",
        "reports/report_configuration_summary.xml",
        "reports/sale_report_view.xml",
        
    ],
    "demo": [],
    "test": [],  # Odoo 17 may still recognize this, but it is optional
    "auto_install": False,
    "application": True,
    "installable": True,
    "license": "LGPL-3",
    "assets": {
        "web.assets_backend": [
            "cpq_sale/static/src/css/custom.css",
            "cpq_sale/static/src/js/sale_product_field.esm.js",
        ],
    },
    # ✅ This tells Odoo where your test files live:
    "unittest": [
        'tests/test_cpq_configuration_hash.py',
    ],
}
