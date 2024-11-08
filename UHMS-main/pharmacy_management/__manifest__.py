{
    'name': 'Pharmacy Management',
    'version': '1.0',
    'category': 'Healthcare',
    'summary': 'Manage medicines, prescriptions, and inventory',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/medicine_views.xml',
        'views/prescription_views.xml',
        'views/inventory_views.xml',
        'views/pharmacy_menus.xml',
        'views/email_templates.xml',
        'reports/inventory_report.xml',
        
    ],
    'installable': True,
    'application': True,
}
