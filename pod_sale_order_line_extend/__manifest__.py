{
    'name': 'Enhanced Sale Order Customization',
    'version': '17.0.1.0',
    'category': 'Sales',
    'summary': 'Advanced Sale Order Customization for Odoo 17',
    'description': """
        Enhance your sale order process in Odoo 17 with features like adding multiple order lines,
        improved UI design, and better product configuration. Ideal for businesses looking to streamline
        their sales workflow and provide a better user experience.
    """,
    'author': 'SPD Solutions Pvt. Ltd.',
    'depends': ['sale_product_configurator', 'sale_management'],
    'assets': {
        'web.assets_backend': [
            'spd_sale_order_line_extend/static/src/**/*',
        ],
    },
    "images": [
        "static/description/banner.png",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}