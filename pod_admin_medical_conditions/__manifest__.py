
{
    'name': 'Podiatry Condition',
    'description': 'Podiatry Medical Condition Module',
    'author': 'NWPL',
    'version': '15.0.0.0.1',
    'website': 'https://nwpodiatric.com',
    'license': 'GPL-3',
    'category': 'Medical',
    'depends': [
        'podiatry_base',
        'podiatry_administration_practitioner',
    ],
    'summary': 'Introduce condition notion into the podiatry category',
    'data': [
        'security/ir.model.access.csv',
        # 'views/podiatry_pathology_view.xml',
        # 'views/podiatry_pathology_category_view.xml',
        'views/podiatry_pathology_group_view.xml',
        'views/podiatry_patient_condition_view.xml',
        'views/podiatry_patient_view.xml',
        'views/podiatry_condition_view.xml',
    ],
    'installable': True,
    'auto_install': False,

}
