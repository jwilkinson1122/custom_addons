# Copyright 2018 GRAP - Sylvain LE GAL
# Copyright 2018 Tecnativa S.L. - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "POS Frontend Orders Management",
    "summary": "Manage old POS Orders from the frontend",
    "version": "15.0.1.1.0",
    "category": "Point of Sale",
    "author": "GRAP, " "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/pos",
    "license": "AGPL-3",
    "depends": ["point_of_sale"],
    "data": [
        "views/view_pos_config.xml",
        "views/view_pos_order.xml",
    ],
    "assets": {
        "point_of_sale.assets": [
            'pos_order_mgmt/static/src/css/pos.css',
            'pos_order_mgmt/static/src/js/widgets.js',
            'pos_order_mgmt/static/src/css/pos.css',
        ],
        'web.assets_qweb': [
            'pos_order_mgmt/static/src/xml/**/*',
        ],
    },
    "application": False,
    "installable": True,
}
