{
    "name": "CPQ",
    "summary": "Dynamic Configure-Price-Quote-style generation of products",
    "author": "NWPL",
    "category": "Sales/Sales",
    "version": "17.0.1.0.0",
    "depends": ["product", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template.xml",
        "views/product_product.xml",
        "views/product_attribute.xml",
    ],
    "demo": [],
    "license": "LGPL-3",
    "assets": {
        "web.assets_backend": [
            "cpq/static/src/components/**/*",
            # Main CPQ components
            # "cpq/static/src/components/**/*",
            # "cpq/static/src/components/dialog/dialog.esm.js",
            # "cpq/static/src/components/dialog/utils.esm.js",
            # "cpq/static/src/components/dialog/configurator_summary_panel.esm.js",
            # "cpq/static/src/components/dialog/product_tmpl_attrib.esm.js",
            # "cpq/static/src/components/dialog/dialog.xml",
            # "cpq/static/src/components/dialog/product_tmpl_attrib.xml",

            # If you have cpq_sale as a separate module:
            # "cpq_sale/static/src/js/product_configurator_widget.esm.js",
        ],
    },
}
