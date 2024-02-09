{
    "name": "Configure Product",
    "author": "NWPL",
    "license": "LGPL-3",
    "website": "https://www.nwpodiatric.com",
    "category": "Hidden",
    "summary": """The system will display Configure Product wizard after
    Adding a product to the sale order and prescriptions order form.
    """,
    "version": "17.0.0.0.0",
    "depends": [
        "sale_product_configurator",
        "pod_prescriptions",
        "sale_management",
    ],
    "data": [
        "views/prescriptions_order_view.xml",
    ],
}
