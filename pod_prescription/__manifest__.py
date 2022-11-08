{
    "name": "Podiatry Patient Prescription",
    "description": "Members can borrow patients from the pod.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": ["pod_member", "mail", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/prescription_mass_message_wizard_view.xml",
        "views/pod_menu.xml",
        "views/prescription_view.xml",
        "views/prescription_kanban_view.xml",  # Ch11
        "data/stage_data.xml",
        # "views/assets.xml",  # Ch11, until Odoo 14
    ],
    "assets": {  # Ch11, since Odoo 15
        "web.assets_backend": {
            "pod_prescription/static/src/css/prescription.css",
            "pod_prescription/static/src/js/prescription.js",
        }
    }
}
