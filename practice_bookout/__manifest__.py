{
    "name": "Practice Prescription Bookout",
    "description": "Practitioners can borrow prescriptions from the practice.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": ["practice_practitioner", "mail", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/bookout_mass_message_wizard_view.xml",
        "views/practice_menu.xml",
        "views/bookout_view.xml",
        "views/bookout_kanban_view.xml",  # Ch11
        "data/stage_data.xml",
        # "views/assets.xml",  # Ch11, until Odoo 14
    ],
    "assets": {  # Ch11, since Odoo 15
        "web.assets_backend": {
            "practice_bookout/static/src/css/bookout.css",
            "practice_bookout/static/src/js/bookout.js",
        }
    }
}
