{
    "name": "Podiatry Prescription Bookout",
    "description": "Podiatry prescriptions.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": ["pod_patient", "mail", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/bookout_mass_message_wizard_view.xml",
        "views/pod_menu.xml",
        "views/bookout_view.xml",
        "views/bookout_kanban_view.xml",  # Ch11
        "data/stage_data.xml",
        # "views/assets.xml",  # Ch11, until Odoo 14
    ],
    "assets": {  # Ch11, since Odoo 15
        "web.assets_backend": {
            "pod_bookout/static/src/css/bookout.css",
            "pod_bookout/static/src/js/bookout.js",
        }
    }
}
