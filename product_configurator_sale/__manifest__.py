# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Product Configurator Sale",
    "version": "15.0.1.0.0",
    "category": "Generic Modules/Sale",
    "summary": "Product configuration interface modules for Sale",
    "author": "Pledra, Odoo Community Association (OCA), Glo Networks",
    "license": "AGPL-3",
    "website": "https://github.com/GlodoUK/product-configurator",
    "depends": ["sale_management", "product_configurator"],
    "data": [
        "security/ir.model.access.csv",
        "data/menu_product.xml",
        "views/sale_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "product_configurator_sale/static/src/css/main.css",
        ],
    },
    # "demo": ["demo/res_partner_demo.xml"],
    "installable": True,
    "auto_install": False,
    "development_status": "Beta",
    "maintainers": ["PCatinean"],
}
