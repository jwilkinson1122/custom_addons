# -*- coding: utf-8 -*-
{
    "name": "Partner Hierarchy",
    "version": "0.1",
    "depends": [
        "contacts",
        "sales_team",
    ],
    "author": "NWPL",
    "license": 'AGPL-3',
    "website": "https://www.nwpodiatric.com",
    "summary": "Manage the hierarchy of partners",
    "description": """Manage the hierarchy of partners""",
    'category': 'Podiatry/Contacts',
    "sequence": 0,
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_view.xml",
        "views/res_partner_type_view.xml",
        "data/res_partner_type_data.xml",
    ],
    "demo": [],
    "auto_install": False,
    "installable": True,
    "application": False,
}
