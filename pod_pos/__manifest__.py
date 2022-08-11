# -*- coding: utf-8 -*-


{
    "name": "Podiatry POS Orthotic Modifier",
    "version": "15.0.0.0",
    "category": "Point of Sale",
    'summary': 'POS product configure',
    "description": """Add Description here.""",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": ['base', 'point_of_sale', 'stock', 'account'],
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
        'point_of_sale.assets': [
            "pod_pos/static/src/css/modifier.css",
            "pod_pos/static/src/js/PodProductScreen.js",
            "pod_pos/static/src/js/ProductTemplateListWidget.js",
            "pod_pos/static/src/js/ProductTemplatePopupWidget.js",
            "pod_pos/static/src/js/screens.js",
            "pod_pos/static/src/js/PodProductList.js",
            "pod_pos/static/src/js/models.js",
            "pod_pos/static/src/js/Popups/ModifierProductPopup.js"
        ],
        'web.assets_qweb': [
            'pod_pos/static/src/xml/**/*',
        ],
    },
    'license': 'OPL-1',
    "auto_install": False,
    "installable": True,
    "images": ['static/description/logo.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
