# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS Pizza Combo Maker/Modifier",
    "version" : "17.0",
    "category" : "Point of Sale",
    'summary': 'POS combo POS combine product pos product combo pos pizza modifier pos product modifier pos pizza combo meal pos combo meal pos meal modifier pos meal product pos make own pizza pos combo maker pos combo modifier pos customize pizza pos customise combo',
    "description": """This odoo app helps user to create pizza product modifier, Add modifier product to modifier groups, set sub products with main modifier products and add to pos cart along with modifier product create bom product add bom sub product quantity and uom and manage stock for bom product. User can select piece of pizza product, and also select modifiers for that, added modifiers also printed on pos receipt. """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.com",
    "price": 89,
    "currency": 'EUR',
    "depends" : ['base','point_of_sale','stock','account','pos_restaurant'],
    "data": [
        'security/ir.model.access.csv',
        'views/product_product.xml',
        'views/bom_product_product_view.xml',
        'views/modifier_product_product_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            "bi_pos_modify_own_pizza/static/src/css/modifier.css",
            "bi_pos_modify_own_pizza/static/src/js/ModifierProductPopup.js",
            "bi_pos_modify_own_pizza/static/src/js/ProductTemplatePopupWidget.js",
            "bi_pos_modify_own_pizza/static/src/js/BiProductScreen.js",
            "bi_pos_modify_own_pizza/static/src/js/screens.js",
            "bi_pos_modify_own_pizza/static/src/js/db.js",
            "bi_pos_modify_own_pizza/static/src/js/BiProductList.js",
            "bi_pos_modify_own_pizza/static/src/js/PartnerScreenExtend.js",
            "bi_pos_modify_own_pizza/static/src/xml/ModifierProductPopup.xml",
            "bi_pos_modify_own_pizza/static/src/xml/pos_new.xml",
        ],
    },
    'license': 'OPL-1',
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/s10F_9PvSyg',
	"images":['static/description/Banner.gif'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
