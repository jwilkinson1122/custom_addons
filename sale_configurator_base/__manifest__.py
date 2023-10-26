{
    "name": "Sale Configurator Base",
    "summary": "Base module for sale configurator",
    "version": "15.0.1.0.2",
    "category": "Uncategorized",
    "website": "https://www.nwpodiatric.com",
    "author": " NWPL",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": [
        "sale"
        ],
    "data": [
        "views/sale_view.xml",
        "templates/sale_report_templates.xml",
        "templates/account_invoice_templates.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'sale_configurator_base/static/src/scss/sale_order.scss',
        ],
    },
    "demo": [],
    "qweb": [],
}
