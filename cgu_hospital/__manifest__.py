{
    'name': "CGU Hospital",

    'summary': """
        Module CGU Hospital functionality:
        #. Doctor Card
        #. Patient card, with the appointment of the main doctor
        #. Document Appointment to the doctor
        #. Document Referral for analysis, with reference to Appointment with a doctor
        #. Document Analysis results
    """,
    'license': 'LGPL-3',

    'description': """
        Keeping records of doctors and patients, documents on doctor's appointments, analysis
            appointments, analysis results
    """,

    'author': "Igor Kuchmar",
    'website': "http://www.ikuchmar.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0
    # /odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/cgu_hospital_groups.xml',
        'security/ir.model.access.csv',
        'security/cgu_hospital_security.xml',
        'views/cgu_hospital_menu.xml',
        'views/cgu_hospital_analysis_direction_views.xml',
        'views/cgu_hospital_analysis_result_views.xml',
        'views/cgu_hospital_analysis_type_views.xml',
        'views/cgu_hospital_doctor_appointment_views.xml',
        'views/cgu_hospital_doctor_views.xml',
        'views/cgu_hospital_patient_views.xml',
        'views/cgu_hospital_speciality_views.xml',
        'report/cgu_hospital_analysis_direction_report.xml',
        'report/cgu_hospital_analysis_direction_report_template.xml',
        'wizard/cgu_hospital_set_doctor_wizard_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'data/cgu_hospital_speciality_demo.xml',
        'data/cgu_hospital_analysis_type_demo.xml',
        'data/cgu_hospital_doctor_demo.xml',
        'data/cgu_hospital_patient_demo.xml',
    ],
}
