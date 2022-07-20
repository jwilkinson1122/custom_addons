# -*- coding: utf-8 -*-


{
    "name": "POS Orthotic Maker/Modifier",
    "version": "15.0.0.0",
    "category": "Point of Sale",
    'summary': 'POS combo POS combine product pos product combo pos orthotic modifier pos product modifier pos orthotic combo meal pos combo meal pos meal modifier pos meal product pos make own orthotic pos combo maker pos combo modifier pos customize orthotic pos customise combo',
    "description": """This odoo app helps user to create orthotic product modifier, Add modifier product to modifier groups, set sub products with main modifier products and add to pos cart along with modifier product create bom product add bom sub product quantity and uom and manage stock for bom product. User can select option of orthotic product, and also select modifiers for that, added modifiers also printed on pos receipt. """,
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
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
