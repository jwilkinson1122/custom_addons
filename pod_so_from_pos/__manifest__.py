{
    'name': 'NWPL - Create SO From POS',
    'version': '17.0.0.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Create sale order from pos screen and view the sales order created fom pos',
    'description': '''
    ''',
    'author': 'NWPL',
    'website': 'http://www.nwpodiatric.com',
    'depends': ['point_of_sale', 'sale_management','web'],
    "data": ['views/pos_config.xml'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pod_create_so_from_pos/static/src/js/Screens/ProductScreen/ControlButtons/SaleOrderButton.js',
            'pod_create_so_from_pos/static/src/js/Screens/ProductScreen/ControlButtons/ViewSalesOrderButton.js',
            'pod_create_so_from_pos/static/src/js/Screens/SaleOrderScreen/SaleOrderScreen.js',
            'pod_create_so_from_pos/static/src/js/Popups/SalesOrderPopup.js',
            'pod_create_so_from_pos/static/src/xml/**/*'
        ],
        # 'point_of_sale.assets': [

        # ],
        
    },
    'images': ['static/description/icon.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'external_dependencies': {
    },
}
