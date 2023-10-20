{
    "name": "Product Configurator Prescription",
    "version": "15.0.1.0.0",
    "category": "Podiatry",
    "summary": "Product configuration for prescriptions",
    "author": "NWPL",
    "license": "AGPL-3",
    "website": "https://www.nwpodiatric.com",
    "depends": ["sale_management", "product_configurator"],
    "data": [
        "security/ir.model.access.csv",
        "data/menu_product.xml",
        "views/prescription_view.xml",
    ],
    # "demo": ["demo/res_partner_demo.xml"],
    "installable": True,
    "auto_install": False,
}
