{
    'name': 'Matrix widget DEMO',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Extra Tools',
    'license': 'OPL-1',
    'version': '17.0.1.0.3',

    'depends': ['kw_matrix_widget', ],
    'data': [
        'security/ir.model.access.csv',
        'demo/demo.xml',
        'views/matrix_views.xml',
    ],

    'installable': True,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],
}
