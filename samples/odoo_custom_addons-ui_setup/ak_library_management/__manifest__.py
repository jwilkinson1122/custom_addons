{
    'name': 'ak library management',
    'version': '18.0.1.0.0',
    'summary': 'Library Management System',
    #'sequence': 10,
    'description': """
its Basic Library management system""",
    'author':'Kajal Barad',
    'category': 'Sales/Sales',
    'website': 'https://www.aktivsoftware.com',
    'depends': ['base','web'],
    'data': [
        'security/ir.model.access.csv',
        'views/library_book_views.xml',
        'views/library_member_views.xml',
        'views/library_book_category_views.xml'
        ],
    'demo': ['base','web'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
