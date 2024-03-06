{
    'name': 'NWPL - Create Prescription Order From POS',
    'version': '17.0.0.0.0',
    'category': 'Prescriptions/Point of Prescription',
    'summary': 'Create prescription order from pos screen and view the prescriptions order created fom pos',
    'description': """ """,
    'author': 'NWPL',
    'website': 'http://www.nwpodiatric.com',
    'depends': [
        'pod_point_of_sale', 
        'prescription_management',
        'web'
        ],
    "data": ['views/pos_config.xml'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pod_prescription_from_pos/static/src/js/Screens/ProductScreen/ControlButtons/PrescriptionOrderButton.js',
            'pod_prescription_from_pos/static/src/js/Screens/ProductScreen/ControlButtons/ViewPrescriptionsOrderButton.js',
            'pod_prescription_from_pos/static/src/js/Screens/PrescriptionOrderScreen/PrescriptionOrderScreen.js',
            'pod_prescription_from_pos/static/src/js/Popups/PrescriptionsOrderPopup.js',
            'pod_prescription_from_pos/static/src/xml/**/*'
        ],
        # 'point_of_sale.assets': [

        # ],
        
    },
    'images': ['static/description/icon.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'external_dependencies': {
    },
}
