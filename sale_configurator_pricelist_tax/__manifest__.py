{
    "name": "Sale Configurator pricelist tax",
    "summary": "Glue module between sale_configurator_base and sale_order_pricelist_tax",
    "version": "15.0.1.0.1",
    "category": "Uncategorized",
    "website": "https://www.nwpodiatric.com",
    "author": "NWPL",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "sale_configurator_base",
        "sale_order_pricelist_tax",
    ],
    "data": ["views/sale_view.xml"],
    "demo": [],
    "auto_install": True,
    "sequence": 10,
}
