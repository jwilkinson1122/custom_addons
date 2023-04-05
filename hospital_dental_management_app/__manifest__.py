
# -*- coding: utf-8 -*-

{
    'name' : 'Hospital Dental Management App',
    'author': "Edge Technologies",
    'version' : '15.0.1.0',
    'live_test_url':'https://youtu.be/QpCmuMWSAmA',
    "images":['static/description/main_screenshot.png'],
    'summary' : 'Dental Clinic Management Healthcare Management Device Management Patient Appointment Doctor Prescription patient Registration Patient Hospitalization Dental hospital management healthcare dental management hospital Odontology healthcare Odontology clinic',
    'description' : """
        Odoo hospital dental clinic management app provides features for complete healthcare management systems like patient details, hospital staff details, patient appointment, patient treatment, patient evaluation, medical prescription, procedures, device management, option management and odontology(dental).
    """,
    'depends' : ['hospital_management_app'],
    "license" : "OPL-1",
    'data' : [

            'security/ir.model.access.csv',
            'views/res_partner_inherited_view.xml',
            'views/appointment_management_inherited_view.xml',
            'views/patient_evaluation_inherited_view.xml',
            'views/patient_procedures_view.xml',
            'views/patient_prescription_inherited_view.xml',
            'views/dental_questionnaire_view.xml',

            ],
    'qweb' : [],
    'demo' : [],
    'installable' : True,
    'auto_install' : False,
    'price': 45,
    'currency': "EUR",
    'category' : 'Healthcare',
}
