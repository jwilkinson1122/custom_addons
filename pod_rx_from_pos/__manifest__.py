{
    'name': 'NWPL - Create RX From POS',
    'version': '17.0.0.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Create prescription ordder from pos screen and view the sales order created fom pos',
    'description': '''
    ''',
    'author': 'NWPL',
    'website': 'http://www.nwpodiatric.com',
    'depends': ['point_of_sale', 'prescription_management','web'],
    "data": ['views/pos_config.xml'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pod_create_rx_from_pos/static/src/js/Screens/ProductScreen/ControlButtons/PrescriptionOrderButton.js',
            'pod_create_rx_from_pos/static/src/js/Screens/ProductScreen/ControlButtons/ViewPrescriptionOrderButton.js',
            'pod_create_rx_from_pos/static/src/js/Screens/PrescriptionOrderScreen/PrescriptionOrderScreen.js',
            'pod_create_rx_from_pos/static/src/js/Popups/PrescriptionOrderPopup.js',
            'pod_create_rx_from_pos/static/src/xml/**/*'
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
