{
    "name": "Configure Product",
    "author": "NWPL",
    "license": "LGPL-3",
    "website": "https://www.nwpodiatric.com",
    "category": "Hidden",
    "summary": """The system will display Configure Product wizard after
    Adding a product to the sale order and prescription order form.
    """,
    "version": "17.0.0.0.0",
    "depends": [
        "sale_product_configurator",
        "prescription",
        "sale_management",
    ],
    "data": [
        "views/prescription_view.xml",
    ],
}
