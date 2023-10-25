
{
    "name": "Sale Configurator Option Typology",
    "summary": "Module to manage Option Typologies",
    "version": "15.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://nwpodiatric.com",
    "author": " NWPL",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["sale_configurator_option"],
    "data": [
        "views/product_view.xml",
        "views/product_configurator_option_view.xml",
        "views/sale_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo": ["demo/product_demo.xml", "demo/sale_demo.xml"],
    "qweb": [],
}
