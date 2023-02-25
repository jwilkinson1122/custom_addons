{
    'name': 'Music Store Application',
    'description': 'Manage music store catalogue',
    'author': 'Iván Causera, Estella Rubio, Antonio Leiva',
    'depends': ['base'],
    'application': True,
    'demo': [
        'data/ir_sequence_data.xml',
        'data/musicstore.song.csv',
        'data/musicstore.artists.csv',
        'data/musicstore.group.csv',
        'data/musicstore.disc.csv',
        'data/musicstore.recordcompany.csv',
        'data/musicstore.sales.csv',
        'data/musicstore.supplies.csv'

    ],
    'data': [
        'security/musicstore_security.xml',
        'security/ir.model.access.csv',
        'views/musicstore_menu.xml',
        'views/song_view.xml',
        'views/group_view.xml',
        'views/artists_view.xml',
        'views/disc_view.xml',
        'views/recordComp_view.xml',
        'views/sales_view.xml',
        'views/supplies_view.xml',
    ]
}
