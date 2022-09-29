{
    "name": "Patients",
    "version": "14.0.1.0",
    "category": "Health Care/Health Care",

    "summary": "Centralize patient information",
    "author": "Miguel Alejandro Guzmán Rodríguez",

    "website": "https://github.com/miguelguzmanr/odoo-healthcare",
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
        "views/hc_root_views.xml",
        "views/res_config_settings_views.xml",
        "views/mail_activity_type_views.xml",

        "views/hc_patient_views.xml",
        "views/hc_patient_civil_status_views.xml",
        "views/hc_patient_education_views.xml",
        "views/hc_patient_occupation_views.xml",

        "views/hc_unit_views.xml",

        "views/hc_type_views.xml",

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
    #         "hc/static/src/**/*",
    #     ],
    # },
    "demo": [],

    "installable": True,
    "application": True,
}
