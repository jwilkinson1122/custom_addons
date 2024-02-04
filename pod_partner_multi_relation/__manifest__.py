{
    "name": "Partner Relations",
    "version": "17.0.0.0.0",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "category": "Podiatry",
    "license": "LGPL-3",
    "depends": [
        "contacts", 
        "sales_team"
        ],
    "demo": ["data/demo.xml"],
    "data": [
        "security/ir.model.access.csv",
        "data/res_partner_type.xml",
        "views/res_partner_relation_all.xml",
        "views/res_partner.xml",
        "views/res_partner_type.xml",
        "views/res_partner_relation_type.xml",
        # "data/res_partner_type.xml",
        "views/menu.xml",
    ],
    "auto_install": False,
    "installable": True,
}
