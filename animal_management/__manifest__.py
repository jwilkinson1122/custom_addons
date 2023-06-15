{
    'name': "Animal Management",
    'summary': "Modul ini digunakan untuk management animal",
    'description': """
        modul ini akan dikembangkan lagi
    """,
    'author': "Dito",
    'website': "http://www.dito.odoo.com",
    'category': 'Uncategorized',
    'version': '14.0.1',
    'depends': ['base', 'base_setup', 'mail', 'product'],
    'data': [
        "security/ir.model.access.csv",
        'views/am_resep_views.xml',
        'views/am_appointment_views.xml',
        'views/am_stage_views.xml',
        'views/am_service_views.xml',
        'views/am_pemeriksaan_views.xml',
        'views/am_menuitem_views.xml',
        
    ],
    
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
