{
    "name": "Clinic Prescription Bookout",
    "description": "Patients can receive prescriptions from the clinic.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": ["clinic_patient", "mail", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/bookout_mass_message_wizard_view.xml",
        "views/clinic_menu.xml",
        "views/bookout_view.xml",
        "views/bookout_kanban_view.xml",  # Ch11
        "data/stage_data.xml",
        # "views/assets.xml",  # Ch11, until Odoo 14
    ],
    "assets": {  # Ch11, since Odoo 15
        "web.assets_backend": {
            "clinic_bookout/static/src/css/bookout.css",
            "clinic_bookout/static/src/js/bookout.js",
        }
    }
}
