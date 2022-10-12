{
    "name": "Patients",
    "version": "15.0.1.0",
    "category": "Health Care/Health Care",

    "summary": "podiatry practice, practitioner, patient and prescription information",
    "author": "NWPL",

    "website": "https://nwpodiatric.com",
    "license": "GPL-3",

    "depends": [
        "base_setup",
        "resource",
        "mail",
    ],

    "data": [
        # ----
        # Data
        # ====
        "data/ir_sequence_data.xml",
        "data/ir_module_category_data.xml",
        # --------
        # Security
        # ========
        "security/res_groups_data.xml",
        "security/ir_model_access_data.xml",
        # -----
        # Views
        # =====
        "views/podiatry_root.xml",
        "views/res_config_settings.xml",
        "views/mail_activity_type.xml",
        "views/podiatry_patient.xml",
        "views/podiatry_patient_shoe_size.xml",
        "views/podiatry_patient_shoe_width.xml",
        "views/podiatry_patient_diagnosis.xml",
        "views/podiatry_patient_weight.xml",
        "views/podiatry_practice.xml",
        "views/podiatry_type.xml",
        "views/podiatry_practitioner.xml",
        "views/podiatry_prescription.xml",
        "views/podiatry_prescription_line.xml",
        "views/podiatry_specialty.xml",
        "views/res_partner.xml",
        # -------
        # Reports
        # =======
        "report/report_view.xml",
        "report/patient_card_report.xml",
        "report/prescription_demo_report.xml",
        # -------
        # Wizards
        # =======
        # "wizard/create_prescription_invoice_wizard.xml",
        # "wizard/create_prescription_shipment_wizard.xml",

    ],

    'assets': {
        'web.assets_backend': [
            'podiatry/static/src/scss/podiatry_practice.scss',
            'podiatry/static/src/scss/card.scss',
        ],
    },
    "demo": [],

    "installable": True,
    "application": True,
}
