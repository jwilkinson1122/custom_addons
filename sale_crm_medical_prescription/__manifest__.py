# Copyright 2016 LasLabs Inc.
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    "name": " Sale CRM - Medical Prescription",
    "summary": "Create opportunities from prescriptions.",
    'author': 'LabViv',
    'version': '13.0.0.0.1',
    'website': 'https://labviv.org.ve/',
    'license': 'GPL-3',
    "category": "Medical",
    "installable": True,
    "depends": [
        "sale_crm",
        "sale_medical_prescription",
    ],
    "data": [
        "wizards/medical_lead_wizard_view.xml",
        "views/crm_lead_view.xml",
    ],
    "demo": [
        "demo/medical_medicament_demo.xml",
        "demo/medical_patient_demo.xml",
        "demo/medical_pharmacy_demo.xml",
        "demo/medical_physician_demo.xml",
        "demo/medical_patient_medication_demo.xml",
        "demo/medical_prescription_order_demo.xml",
        "demo/medical_prescription_order_line_demo.xml",
        "demo/crm_lead_demo.xml",
    ],
    'maintainer': 'Reydi Hernández <rhe@mastercore.net>'
}
