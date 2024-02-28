{
    "name": "NWPL - Partner Multi Relations",
    "version": "17.0.0.0.0",
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "category": "Contacts",
    "license": "AGPL-3",
    "depends": ["contacts", "sales_team"],
    "demo": ["data/demo.xml"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_relation_all.xml",
        "views/res_partner.xml",
        "views/res_partner_relation_type.xml",
        "views/menu.xml",
    ],
    "auto_install": False,
    "installable": True,
}
