# -*- coding: utf-8 -*-
{
    "name": """NWPL - Disable options in POS""",
    "summary": """Control access to POS options""",
    "category": "Point of Sale",
    "images": ["description/icon.png"],
    "version": "17.0.0.0.0",
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "license": "LGPL-3", 
    "depends": [
        "pod_pos_disable_payment", 
        "pos_restaurant", 
        "web_tour"
        ],
    "data": [
        "views/view.xml",
        ],
    "assets": {
        "web.assets_backend": [
            "pod_pos_disable_payment_restaurant/static/src/js/tour_pos_dis_pay_rest.js",
        ],
        "point_of_sale.assets": [
            "pod_pos_disable_payment_restaurant/static/src/js/pos_disable_payment_restaurant.js",
        ],
    },
    "demo": [],
    "application": False,
    "auto_install": False,
    "installable": True,
}