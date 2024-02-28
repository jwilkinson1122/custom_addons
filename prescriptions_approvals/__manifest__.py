

{
    'name': 'NWPL - Prescriptions - Approvals',
    'version': '17.0.0.0.0',
    'category': 'Medical/Prescriptions',
    'summary': 'Approval from prescriptions',
    'description': """
Adds approvals data to prescriptions
""",
    'author': "NWPL",
    'website': 'https://www.nwpodiatric.com',
    'depends': ['prescriptions', 'approvals'],
    'data': [
        "views/res_config_settings_views.xml",
        "views/approval_request_views.xml",
        "data/prescriptions_folder_data.xml",
        "data/prescriptions_facet_data.xml",
        "data/res_company_data.xml"
    ],
    'installable': True,
    'auto_install': True,
    # 'auto_install': False,
    'license': 'LGPL-3',
}
