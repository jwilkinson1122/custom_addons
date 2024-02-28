# -*- coding: utf-8 -*-


{
    'name': 'NWPL - Prescriptions - Signatures',
    'version': '17.0.0.0.0',
    'category': 'Medical/Prescriptions',
    'summary': 'Signature templates from Prescriptions',
    'description': """
Add the ability to create signatures from the prescription module.
The first element of the selection (in DRM) will be used as the signature attachment.
""",
    'author': "NWPL",
    'website': 'https://www.nwpodiatric.com',
    'depends': ['prescriptions', 'sign'],

    'data': [
        'data/prescriptions_workflow_rule_data.xml',
        'views/sign_templates.xml',
        'views/res_config_settings.xml',
    ],

    'demo': [
        'demo/prescriptions_prescription_demo.xml',
    ],

    'installable': True,
    'auto_install': True,
    # 'auto_install': False,
    'license': 'LGPL-3',
}
