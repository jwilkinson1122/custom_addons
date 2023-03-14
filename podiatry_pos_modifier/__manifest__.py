# -*- coding: utf-8 -*-

{
    "name" : "Device Maker/Modifier",
    "version" : "15.0.0.0",
    "category" : "Point of Sale",
    'summary': 'POS product/device modifier',
    "description": """Helps user to create device product modifier""",
    "author": "NWPL",
    "website" : "https://www.nwpodiatric.com",
    "depends" : ['base','point_of_sale','stock','account'],
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
            "podiatry_pos_modifier/static/src/css/modifier.css",
            "podiatry_pos_modifier/static/src/js/BiProductScreen.js",
            "podiatry_pos_modifier/static/src/js/ProductTemplateListWidget.js",
            "podiatry_pos_modifier/static/src/js/ProductTemplatePopupWidget.js",
            "podiatry_pos_modifier/static/src/js/screens.js",
            "podiatry_pos_modifier/static/src/js/BiProductList.js",
            "podiatry_pos_modifier/static/src/js/models.js",
            "podiatry_pos_modifier/static/src/js/Popups/ModifierProductPopup.js"
        ],
        'web.assets_qweb': [
            'podiatry_pos_modifier/static/src/xml/**/*',
        ],
    },
    'license': 'OPL-1',
    "auto_install": False,
    "installable": True,
	"images":['static/description/icon.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
