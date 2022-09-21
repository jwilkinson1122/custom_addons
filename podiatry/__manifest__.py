# See LICENSE file for full copyright and licensing details.

{
    'name': 'Podiatry',
    'version': '15.0.1.0.0',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'category': 'Podiatry Management',
    'license': "AGPL-3",
    'complexity': 'easy',
    'Summary': 'A Module For Podiatry Management',
    'images': ['static/description/company_logo.png'],
    'depends': ['hr', 'crm', 'account'],
    'data': ['security/podiatry_security.xml',
             'security/ir.model.access.csv',
             'data/patient_sequence.xml',
             'data/location_sequence.xml',
             'data/mail_template.xml',
             'wizard/delete_reason_view.xml',
             'views/patient_view.xml',
             'views/podiatry_view.xml',
             'views/hcp_view.xml',
             'views/doctor_view.xml',
             'wizard/assign_roll_no_wizard.xml',
             'wizard/move_standards_view.xml',
             'report/report_view.xml',
             'report/identity_card.xml',
             "report/hcp_identity_card.xml",
             ],
    'demo': ['demo/podiatry_demo.xml'],
    'assets': {
        'web.assets_backend': [
            '/podiatry/static/src/scss/podiatrycss.scss',
        ],
    },
    'installable': True,
    'application': True
}
