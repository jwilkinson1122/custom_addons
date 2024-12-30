{
    'name': 'Hello World App',
    'version': '1.0',
    'summary': 'A custom app for demonstration',
    'description': 'This is a demo app built in Odoo 17.',
    'author': 'cute_Duck',
    'depends': ['base'],
    'data': [
        'views/duckstore_view.xml',
    ],
    'installable': True,
    'application': True,
}