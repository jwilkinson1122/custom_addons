# __manifest__.py
{
    'name': 'Patient Management',
    'version': '1.0',
    'category': 'Healthcare',
    'summary': 'Manage patient information and healthcare services.',
    'description': 'This module manages patient data, appointments, medical histories, treatments, surgeries, and lab tests.',
    'depends': ['base', 'hr'],  # Add any other necessary dependencies
    'data': [
        'security/ir.model.access.csv',
        'views/patients/hospital_patient_views.xml',
        'views/patients/hospital_medical_history_views.xml',
        'views/patients/hospital_appointment_views.xml',
        'views/patients/hospital_treatment_views.xml',
        'views/patients/hospital_surgery_views.xml',
        'views/patients/hospital_lab_test_views.xml',
        'views/patients/hospital_menus.xml',
    ],
    'installable': True,
    'application': True,
}
