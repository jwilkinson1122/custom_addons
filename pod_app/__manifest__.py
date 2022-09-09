# -*- coding: utf-8 -*-


{

    "name": "Podiatry Management System",
    "version": "15.0.0.0",
    "summary": "Manage patients, doctors, prescriptions for manufacturing custom podiatry devices",
    "category": "Podiatry",
    "description": """
 
    custom orthotics manufacturing management system
 
""",
    "depends": ["base", "sale_management", "stock", "account"],
    "data": [
        'security/practice_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/assets.xml',
        'views/login_page.xml',
        'views/main_menu_file.xml',
        'wizard/podiatry_appointments_invoice_wizard.xml',
        'wizard/create_prescription_invoice_wizard.xml',
        'wizard/create_prescription_shipment_wizard.xml',
        'views/podiatry_treatment.xml',
        'views/podiatry_drug_route.xml',
        'wizard/podiatry_lab_test_create_wizard.xml',
        'wizard/podiatry_lab_test_invoice_wizard.xml',
        'views/podiatry_prescription_order.xml',
        'views/podiatry_directions.xml',
        'views/podiatry_dose_unit.xml',
        'views/podiatry_patient_evaluation.xml',
        'views/podiatry_family_condition.xml',
        'views/podiatry_inpatient_registration.xml',
        'views/podiatry_inpatient_device.xml',
        'views/podiatry_insurance_plan.xml',
        'views/podiatry_appointment.xml',
        'views/podiatry_insurance.xml',
        'views/podiatry_patient_lab_test.xml',
        'views/podiatry_lab_test_units.xml',
        'views/podiatry_lab.xml',
        'views/podiatry_neomatal_apgar.xml',
        'views/podiatry_pathology_category.xml',
        'views/podiatry_pathology_group.xml',
        'views/podiatry_pathology.xml',
        'views/podiatry_patient_condition.xml',
        'views/podiatry_patient_device.xml',
        'views/podiatry_patient_device1.xml',
        'views/podiatry_patient_pregnancy.xml',
        'views/podiatry_patient_prental_evolution.xml',
        'views/podiatry_patient.xml',
        'views/podiatry_physician.xml',
        'views/podiatry_preinatal.xml',
        'views/podiatry_prescription_line.xml',
        'views/podiatry_puerperium_monitor.xml',
        'views/podiatry_rcri.xml',
        'views/podiatry_rounding_procedure.xml',
        'views/podiatry_test_critearea.xml',
        'views/podiatry_test_type.xml',
        'views/podiatry_vaccination.xml',
        'views/res_partner.xml',
        'report/report_view.xml',
        'report/appointment_recipts_report_template.xml',
        'report/podiatry_view_report_document_lab.xml',
        'report/podiatry_view_report_lab_result_demo_report.xml',
        'report/newborn_card_report.xml',
        'report/patient_card_report.xml',
        'report/patient_conditions_document_report.xml',
        'report/patient_devices_document_report.xml',
        'report/patient_vaccinations_document_report.xml',
        'report/prescription_demo_report.xml',
    ],

    "assets": {
        "web.assets": [
            "pod_app/static/src/css/style.css",
        ],

    },

    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "installable": True,
    "application": True,
    "auto_install": False,
    "images": ["static/description/logo.png"],
    "license": 'OPL-1',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
