{
    "name": "estate",
    "version": "1.0",
    "depends": ["base"],
    "author": "Bagus",
    "installable": True,
    "application": True,
    "auto_install": False,
    "data": [
        # Model data
        "data/res_partner_data.xml",
        "data/estate_property_type_data.xml",
        # Depends on `res_partner_data.xml`, `estate_property_type_data.xml`
        "data/estate_property_data.xml",
        "data/estate_tag_data.xml",
        # Security
        "security/ir.model.access.csv",
        # Views
        "views/estate_offer_views.xml",
        "views/estate_property_views.xml",
        "views/estate_property_type_views.xml",
        "views/estate_tag_views.xml",
        
        "views/actions.xml",
        "views/menus.xml",  # Depends on `actions.xml`
    ],
}
