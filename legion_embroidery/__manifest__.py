# -*- coding: utf-8 -*-
{
    'name': "Embroidery",
    'summary': """Embroidery Manufacturing""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Byte Legion",
    'website': "http://www.erp.bytelegions.com",
    'category': 'Manufacturing',
    'version': '17.0.0.0.0',
    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'stock', 'contacts'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/menus.xml',
        'views/embroidery_view.xml',
        'views/product_view.xml',
        'views/embroidery_bom_view.xml',
        'views/embroidery_scrap_view.xml',

        'data/sequence.xml',
        # 'data/auto_invoice_post.xml',

        # 'report/report_menus.xml',
        'report/report_formats.xml',
        'report/emb_report_template_view.xml',
        'report/bom_report_template_view.xml',

        'report/emb_reporting.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'images': ['static/description/banner.gif']
}
