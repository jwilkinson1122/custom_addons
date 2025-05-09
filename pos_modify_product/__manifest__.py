# -*- coding: utf-8 -*-


{
    "name" : "POS Product Modifier",
    "version" : "17.0",
    "category" : "Point of Sale",
    "author": "NWPL",
    "website" : "https://www.nwpodiatric.com",
    "depends" : [
        'base',
        'point_of_sale',
        'stock',
        'account',
        'pos_sale',
        ],
    "data": [
        'security/ir.model.access.csv',
        'views/product_product.xml',
        'views/bom_product_product_view.xml',
        'views/modifier_product_product_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            "pos_modify_product/static/src/css/modifier.css",
            "pos_modify_product/static/src/js/product_modifier_popup.js",
            "pos_modify_product/static/src/js/product_template_popup.js",
            "pos_modify_product/static/src/js/product_screen.js",
            "pos_modify_product/static/src/js/models.js",
            "pos_modify_product/static/src/js/db.js",
            "pos_modify_product/static/src/js/products_widget.js",
            "pos_modify_product/static/src/js/partner_list_screen.js",
            "pos_modify_product/static/src/xml/product_modifier_popup.xml",
            "pos_modify_product/static/src/xml/pos_new.xml",
        ],
    },
    'license': 'OPL-1',
    "auto_install": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
