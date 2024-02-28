

{
    'name': 'NWPL - Prescriptions - Project - Sale',
    'version': '17.0.0.0.0',
    'category': 'Medical/Prescriptions',
    'summary': 'Products Workspace Templates',
    'description': """
Adds the ability to set workspace templates on products.
""",
    'depends': ['prescriptions_project', 'sale_project'],
    'data': [
        'views/product_views.xml',
    ],
    'demo': [
        'data/prescriptions_demo.xml',
        'data/project_sale_demo.xml',
    ],
    'auto_install': True,
    'license': 'LGPL-3',
}
