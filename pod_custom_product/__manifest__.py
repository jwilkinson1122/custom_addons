# -*- coding: utf-8 -*-

{
    "name" : "POD Custom Product Modifier",
    "version" : "15.0.0.0",
    "category" : "Podiatry",
    'summary': 'Customize or modify orthotics',
    "description": """This app helps user to create orthotics product modifier, Add modifier product to modifier groups, set sub products with main modifier products and add to cart along with modifier product create bom product add bom sub product quantity and uom and manage stock for bom product. User can select sides of the orthotic product, and also select modifiers for that, added modifiers also printed. """,
    "author": "NWPL",
    "website" : "https://www.nwpodiatric.com",
    "depends" : [
        'base',
        'sale',
        'sale_management'
        'stock',
        'account'
        ],
    "data": [
        'security/ir.model.access.csv',
        'views/product_product.xml',
        'views/bom_product_product_view.xml',
        'views/modifier_product_product_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos_new.xml',
        'static/src/xml/ModifierProductPopup.xml',
    ],
    'assets': {
        'web.assets_backend': [
            "pod_custom_product/static/src/css/modifier.css",
            "pod_custom_product/static/src/js/PodProductScreen.js",
            "pod_custom_product/static/src/js/ProductTemplateListWidget.js",
            "pod_custom_product/static/src/js/ProductTemplatePopupWidget.js",
            "pod_custom_product/static/src/js/screens.js",
            "pod_custom_product/static/src/js/PodProductList.js",
            "pod_custom_product/static/src/js/models.js",
            "pod_custom_product/static/src/js/Popups/ModifierProductPopup.js"
        ],
        'web.assets_qweb': [
            'pod_custom_product/static/src/xml/**/*',
        ],
    },
    "license": "LGPL-3",
    "auto_install": False,
    "installable": True,
}

