{
    "name": "CPQ Attribute Set",
    "author": "NWPL",
    "version": "17.0.1.3.0",
    "category": "Generic Modules/Others",
    "license": "AGPL-3",
    "depends": ["base", "base_sparse_field"],
    "data": [
        "security/ir.model.access.csv",
        "security/attribute_security.xml",
        # "views/menu_view.xml",
        "views/attribute_attribute_view.xml",
        "views/attribute_group_view.xml",
        "views/attribute_option_view.xml",
        "views/attribute_set_view.xml",
        "views/menu_view.xml",
        "wizard/attribute_option_wizard_view.xml",
        
    ],
    "external_dependencies": {"python": ["unidecode"]},
    "installable": True,
}
