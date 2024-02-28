# -*- coding: utf-8 -*-


{
    'name': 'NWPL - Prescriptions Project Sign',
    'version': '17.0.0.0.0',
    'category': 'Medical/Prescriptions',
    'summary': 'Sign prescriptions attached to tasks',
    'description': """
Adds an action to sign prescriptions attached to tasks.
""",
    'website': ' ',
    'depends': ['prescriptions_project', 'prescriptions_sign'],
    'data': [
        'data/prescriptions_workflow_rule_data.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
