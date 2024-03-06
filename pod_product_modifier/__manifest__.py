# -*- coding: utf-8 -*-


{
    "name" : "NWPL - POS Product Modifier",
    "version" : "17.0.0.0.0",
    "category" : "Point of Sale",
    'summary': 'Product modifier',
    "description": """Add modifier product to modifier groups, set sub products with main modifier products.""",
    "author": "NWPL",
    "website" : "https://www.nwpodiatric.com",
    "depends" : [
        'base',
        'pod_point_of_sale',
        'pod_prescription',
        'pod_prescription_management',
        'sale',
        'sale_management',
        'stock',
        'account',
        # 'pos_restaurant'
        ],
    "data": [
        'security/ir.model.access.csv',
        'views/product_product.xml',
        'views/bom_product_product_view.xml',
        'views/modifier_product_product_view.xml',
    ],
    'assets': {
        'pod_point_of_sale._assets_pos': [
            "pod_product_modifier/static/src/css/modifier.css",
            "pod_product_modifier/static/src/js/ModifierProductPopup.js",
            "pod_product_modifier/static/src/js/ProductTemplatePopupWidget.js",
            "pod_product_modifier/static/src/js/ProductScreen.js",
            "pod_product_modifier/static/src/js/screens.js",
            "pod_product_modifier/static/src/js/db.js",
            "pod_product_modifier/static/src/js/ProductList.js",
            "pod_product_modifier/static/src/js/PartnerScreenExtend.js",
            "pod_product_modifier/static/src/xml/ModifierProductPopup.xml",
            "pod_product_modifier/static/src/xml/pos_new.xml",
        ],
    },
    'license': 'OPL-1',
    "auto_install": False,
    "installable": True,
	"images":['static/description/icon.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
