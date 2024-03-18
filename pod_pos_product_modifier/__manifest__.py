# -*- coding: utf-8 -*-


{
    "name" : "NWPL - Product Modifier",
    "version" : "17.0.0.0.0",
    "category" : "Point of Sale",
    'summary': 'product modifier',
    "description": """ """,
    "author": "NWPL",
    "website" : "https://www.nwpodiatric.com",
    "depends" : [
        'base',
        'point_of_sale',
        'stock',
        'account',
        # 'pos_restaurant'
        ],
    "data": [
        'security/ir.model.access.csv',
        'views/product_product.xml',
        'views/bom_product_product_view.xml',
        'views/modifier_product_product_view.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            # "pod_pos_product_modifier/static/src/css/modifier.css",
            "pod_pos_product_modifier/static/src/scss/modifier.scss",
            "pod_pos_product_modifier/static/src/js/modifier_product_popup.js",
            "pod_pos_product_modifier/static/src/js/product_template_popup.js",
            "pod_pos_product_modifier/static/src/js/product_screen.js",
            "pod_pos_product_modifier/static/src/js/screens.js",
            "pod_pos_product_modifier/static/src/js/db.js",
            "pod_pos_product_modifier/static/src/js/product_list.js",
            "pod_pos_product_modifier/static/src/js/partner_screen_extend.js",
            "pod_pos_product_modifier/static/src/xml/modifier_product_popup.xml",
            "pod_pos_product_modifier/static/src/xml/pos_new.xml",
        ],
    },
    'license': 'LGPL-3',
    "auto_install": False,
    "installable": True,
	"images":['static/description/icon.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
