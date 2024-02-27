{
    "name": "NWPL - Pos Print Sales Orders",
    "version": "17.0.0.0.0",
    "category": "Sales/Point of Sale",
    "summary": "Print multiple sale orders in POS",
    "depends": [
        "point_of_sale", 
        "pos_sale"
        "pod_prescription"
        ],
    "website": "https://www.nwpodiatric.com",
    "author": "NWPL",
    "images": ["static/description/icon.png"],
    "installable": True,
    "data": ["views/res_config_settings_view.xml"],
    "assets": {
        "point_of_sale.assets": [
            "pod_pos_sale_order_print/static/src/js/pod_pos_sale_order_print.esm.js",
            "pod_pos_sale_order_print/static/src/js/SaleOrderManagementScreen.esm.js",
        ],
    },
    "license": "LGPL-3",
}
