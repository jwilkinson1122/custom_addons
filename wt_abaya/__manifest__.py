{
    'name': 'Abaya',
    'version': '17.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Abaya shop is a tailoring and retail shop with local and international business',
    'description': """
            Abaya shop is a tailoring and retail shop with local and international business. The
            actual customer will order through phone or by actual shop visit. The product type will be Abaya and their
            will be different variants available with change in color, design, cost etc. The ordered item will be ready
            in a couple of days as per the staff availability and the customer is notified for delivery (shop pick-up or
            home delivery). Also the Abaya shop is exporting products using different couriers such as DHL, Aramex. 
            """,
    'author': 'Warlock Technologies Pvt Ltd.',
    'website': 'http://warlocktechnologies.com',
    'support': 'support@warlocktechnologies.com',
    'depends': ['web', 'point_of_sale','product'],
    'data': [
        'security/ir.model.access.csv',
        'views/measurment.xml',
        'views/pos_categories.xml',
        'views/res_partner.xml',
        'views/product.xml',
        'views/pos_order.xml',
        'views/menu.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            "/wt_abaya/static/src/css/style.css",
            '/wt_abaya/static/src/xml/partner_line.xml',
            '/wt_abaya/static/src/xml/measurment_popup.xml',
            '/wt_abaya/static/src/xml/set_measurment.xml',
            '/wt_abaya/static/src/xml/product_screen.xml',
            '/wt_abaya/static/src/js/xml/**/*',
            
        ],
    },
    
    'images': ['images/screen_image.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 100.00,
    'currency': 'USD',
    'external_dependencies': {
    },
}

