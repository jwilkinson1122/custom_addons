{
    "name": "Podiatry Item Checkout",
    "description": "Members can borrow items from the pod.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": ["pod_member", "mail", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/checkout_mass_message_wizard_view.xml",
        "views/pod_menu.xml",
        "views/checkout_view.xml",
        "views/checkout_kanban_view.xml",  # Ch11
        "data/stage_data.xml",
        # "views/assets.xml",  # Ch11, until Odoo 14
    ],
    "assets": {  # Ch11, since Odoo 15
        "web.assets_backend": {
            "pod_checkout/static/src/css/checkout.css",
            "pod_checkout/static/src/js/checkout.js",
        }
    }
}
