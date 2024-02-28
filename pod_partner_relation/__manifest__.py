{
    "name": "NWPL - Partner relations",
    "version": "17.0.0.0.0",
    "author": "NWPL",
    "category": "Contacts",
    "license": "AGPL-3",
    "website": "https://www.nwpodiatric.com",
    "depends": [
        'sales_team',
    ],
    "demo": [
        "data/demo.xml",
    ],
    "data": [
        "views/res_partner_relation_all.xml",
        'views/res_partner.xml',
        'views/res_partner_relation_type.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
    ],
    "auto_install": False,
    "installable": True,
}
