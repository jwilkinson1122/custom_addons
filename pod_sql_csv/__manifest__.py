# -*- coding: utf-8 -*-
{
    'name': "SQL To CSV",

    'summary': """
        Get the data you want from your database, from SQL to CSV.""",

    'description': """
        Head to Settings -> Technical -> SQL to CSV.
        There you will be able to export the data you want from your database, with SQL, to a CSV file.
    """,
    'license': "OPL-1",
    'category': 'Administration',
    'version': '1.0',
    'images': ['static/description/main_screenshot.png',],
    'support': 'lop@nalios.be',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/sql_to_csv_views.xml',
    ],
}
