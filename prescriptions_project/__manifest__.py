# -*- coding: utf-8 -*-


{
    'name': 'NWPL - Prescriptions - Projects',
    'version': '17.0.0.0.0',
    'category': 'Medical/Prescriptions',
    'summary': 'Project from prescriptions',
    'description': """
Add the ability to create invoices from the prescription module.
""",
    'author': "NWPL",
    'website': 'https://www.nwpodiatric.com',
    'depends': ['prescriptions', 'project'],
    'data': [
        'data/prescriptions_folder_data.xml',
        'data/prescriptions_facet_data.xml',
        'data/prescriptions_tag_data.xml',
        'data/prescriptions_workflow_data.xml',
        'views/prescriptions_folder_views.xml',
        'views/prescriptions_facet_views.xml',
        'views/prescriptions_tag_views.xml',
        'views/prescriptions_prescription_views.xml',
        'views/project_views.xml',
        'views/prescriptions_templates_share.xml',
        'views/project_templates.xml',
    ],
    'demo': [
        'data/prescriptions_project_demo.xml',
    ],
    'auto_install': True,
    # 'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': '_prescriptions_project_post_init',
}
