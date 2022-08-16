# Copyright 2017 LasLabs Inc.
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html)

{
    "name": "Medical Prescription Sales",
    "summary": "Create sale orders from prescriptions.",
    'author': 'LabViv',
    'version': '13.0.0.0.1',
    'website': 'https://labviv.org.ve/',
    'license': 'GPL-3',
    "category": "Medical",
    "installable": True,
    "depends": [
        "sale",
        "stock",
        "medical_prescription",
        "medical_pharmacy",
        "medical_physician",
        "medical_prescription_thread",
    ],
    "data": [
        "data/product_category_data.xml",
        "views/medical_pharmacy_view.xml",
        "views/medical_medicament_view.xml",
        "views/prescription_order_line_view.xml",
        "views/prescription_order_view.xml",
        "views/sale_order_view.xml",
        "views/medical_physician_view.xml",
        "views/medical_patient_view.xml",
        "wizards/medical_sale_wizard_view.xml",
        "wizards/medical_sale_temp_view.xml",
    ],
    "demo": [
        "demo/product_category_demo.xml",
        "demo/medical_patient_demo.xml",
        "demo/medical_medicament_demo.xml",
        "demo/medical_physician_demo.xml",
        "demo/medical_pharmacy_demo.xml",
        "demo/medical_patient_medication_demo.xml",
        "demo/medical_prescription_order_demo.xml",
        "demo/medical_prescription_order_line_demo.xml",
        "demo/sale_order_demo.xml",
        "demo/sale_order_line_demo.xml",
    ],
    'maintainer': 'Reydi Hernández <rhe@mastercore.net>'
}
