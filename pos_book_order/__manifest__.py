{
    'name': 'POS Booking Order',
    'version': '12.0.1.0.0',
    'summary': """Book orders in pos""",
    'description': 'Book orders for customers in POS',
    'category': 'Point of Sale',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/pos_config.xml',
        'views/book_order.xml',
        'security/ir.model.access.csv'
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_book_order/static/src/js/book_order.js',
            'pos_book_order/static/src/js/popup.js',
            'pos_book_order/static/src/js/booked_order.js',
            'pos_book_order/static/src/js/delivery_orders.js',
            'pos_book_order/static/src/js/pickup_orders.js',
            'pos_book_order/static/src/js/models.js',
        ],
        'web.assets_qweb': [
            'pos_book_order/static/src/xml/**/*',
        ],
        # 'web.assets_qweb': [
        #     'static/src/xml/book_order.xml',
        #     'static/src/xml/booked_order.xml',
        #     'static/src/xml/pickup_orders.xml',
        #     'static/src/xml/delivery_orders.xml',
        # ],
    },
    'demo': [],
    'images': ['static/description/images/banner.png'],
    # 'qweb': ['static/src/xml/book_order.xml',
    #          'static/src/xml/booked_order.xml',
    #          'static/src/xml/pickup_orders.xml',
    #          'static/src/xml/delivery_orders.xml'
    #          ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
}

# <script type="text/javascript" src="/pos_book_order/static/src/js/book_order.js"/>
# <script type="text/javascript" src="/pos_book_order/static/src/js/popup.js"/>
# <script type="text/javascript" src="/pos_book_order/static/src/js/booked_order.js"/>
# <script type="text/javascript" src="/pos_book_order/static/src/js/delivery_orders.js"/>
# <script type="text/javascript" src="/pos_book_order/static/src/js/pickup_orders.js"/>
# <script type="text/javascript" src="/pos_book_order/static/src/js/models.js"/>
