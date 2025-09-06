
{
    "name": "Sales Product Set Sell only by packaging",
    "version": "17.0.1.0.0",
    "category": "Sales",
    "license": "AGPL-3",
    # "installable": True,
    # "auto_install": True,
    "depends": ["sell_only_by_packaging", "sale_product_set_packaging_qty"],
    "data": [
        "data/ir_cron.xml",
        "views/product_set_line.xml",
        "views/product_template.xml",
    ],
}
