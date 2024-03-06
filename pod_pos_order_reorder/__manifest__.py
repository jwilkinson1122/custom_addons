{
    "name": "NWPL - Pos Re-order",
    "version": "17.0.0.0.0",
    "category": "Sales/Point of Sale",
    "summary": "Re-order in the Point of Sale ",
    "depends": ["pod_point_of_sale"],
    "website": "https://www.nwpodiatric.com",
    "author": "NWPL",
    "images": ["static/description/icon.png"],
    "data": [
        "views/res_config_settings_view.xml",
    ],
    "installable": True,
    "assets": {
        "point_of_sale.assets": [
            "pod_pos_order_reorder/static/src/js/**/*.js",
            "pod_pos_order_reorder/static/src/xml/**/*.xml",
        ],
    },
    "license": "LGPL-3",
}
