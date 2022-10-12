{
    "name": "Podiatry Prescription Checkout",
    "description": "Practitioners can borrow prescriptions from the podiatry.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": ["podiatry_practitioner", "mail", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/checkout_mass_message_wizard_view.xml",
        "views/podiatry_menu.xml",
        "views/checkout_view.xml",
        "views/checkout_kanban_view.xml",  
        "data/stage_data.xml",
 
    ],
    "assets": {   
        "web.assets_backend": {
            "podiatry_checkout/static/src/css/checkout.css",
            "podiatry_checkout/static/src/js/checkout.js",
        }
    }
}
