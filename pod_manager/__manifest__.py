# -*- coding: utf-8 -*-
{
    'name': "Podiatry Manager",

    'summary': """
        Module for managing podiatry practice  staff, patient information 
        and custom order management.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "NWPL Dev",
    'website': "http://www.nwpodiatric.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Practice',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management', 'stock', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'security/pod_practice_groups.xml',
        'views/assets.xml',
        'views/pod_doctor.xml',
        'views/pod_order.xml',
        'views/pod_order_details.xml',
        'views/pod_patient.xml',
        'views/pod_patient_condition.xml',
        'views/pod_patient_device.xml',
        'views/pod_patient_device1.xml',
        'views/pod_menu_file.xml',
        'views/pod_login_page.xml',
        'views/pod_pathology_category.xml',
        'views/pod_pathology_group.xml',
        'views/pod_pathology.xml',
        'views/res_partner.xml',
        'report/pod_patient_info_report.xml',
        # 'wizards/pod_order_invoice.xml',
        # 'wizards/pod_order_shipment.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #    'demo/demo.xml',
    # ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "images": ["static/description/full_logo1"],
    # "live_test_url": '',
    # "license": ' ',
}
