
{
    "name": "Sales product set",
    "category": "Sales",
    "license": "AGPL-3",
    "version": "17.0.1.0.0",
    "depends": ["sale", "sale_management", "product_set"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_set.xml",
        "views/product_set_line.xml",
        "wizard/sale_product_set_wizard_view.xml",
        "views/sale_order.xml",
        "views/res_config_settings.xml",
    ],
    "demo": ["demo/product_set_line.xml"],
    "installable": True,
}
