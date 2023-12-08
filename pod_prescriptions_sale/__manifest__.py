# -*- coding: utf-8 -*-

{
    'name' : "NWPL Prescriptions to Sales",
    'version' : "17.0.0.1",
    'category' : "Sales",
    'license': 'LGPL-3',
    'summary': 'This apps helps to Convert Prescription Orders to Sales Orders',
    'description' : """Create Sales Orders from confimed Prescription Orders""",
    'author' : "NWPL",
    'website'  : "https://www.nwpodiatric.com",
    'depends' : [ 
        'base', 
        'product',
        'sale_management',
        'pod_prescriptions',
        'stock'
        ],    
    'data' : [
            'security/ir.model.access.csv',
            'wizard/sale_order_wizard_view.xml',
            'views/main_prescription_order_view.xml',
            ],

    'test' :  [ ],
    'css'  :  [ ],
    'demo' :  [ ],
    'installable' : True,
    'application' :  False,
}
