{
    "name": "Patients",
    "version": "15.0.1.0",
    "category": "Health Care/Health Care",

    "summary": "podiatry practice, doctor, patient and prescription information",
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
        "views/podiatry_root_views.xml",
        "views/res_config_settings_views.xml",
        "views/mail_activity_type_views.xml",
        "views/podiatry_patient_views.xml",
        "views/podiatry_patient_shoe_size_views.xml",
        "views/podiatry_patient_shoe_width_views.xml",
        "views/podiatry_patient_diagnosis_views.xml",
        "views/podiatry_patient_weight_views.xml",
        "views/podiatry_practice_views.xml",
        "views/podiatry_type_views.xml",
        "views/res_partner_views.xml",

        # -------
        # Reports
        # =======

        # -------
        # Wizards
        # =======

    ],

    # "assets": {
    #     "web.assets_backend": [
    #         "podiatry/static/src/**/*",
    #     ],
    # },
    "demo": [],

    "installable": True,
    "application": True,
}
