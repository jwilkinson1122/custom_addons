# -*- coding: utf-8 -*-
{
    "name": "Partner Organisation",
    "version": "0.1",
    "depends": [
        "contacts",
        "sales_team",
    ],
    "author": "Smile",
    "license": 'AGPL-3',
    "website": "https://www.smile.eu/",
    "summary": "Manage the hierarchy of partners",
    "description": """
Partner Organisation
=====================
    """,
    'category': 'Organisation',
    "sequence": 0,
    "data": [
        "security/ir.model.access.csv",
        # "views/kanban_template_view.xml",
        "views/res_partner_view.xml",
        "views/res_partner_type_view.xml",
        "data/res_partner_type_data.xml",
    ],
    "demo": [],
    "auto_install": False,
    "installable": True,
    "application": False,
}
