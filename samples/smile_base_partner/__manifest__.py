# -*- coding: utf-8 -*-
{
    "name": "Partner Hierarchies",
    "version": "0.1",
    "depends": [
        "base",
        "base_setup",
        # "phone_validation",
        "mail",
        # "resource",
        "web",
        "web_hierarchy",
        "contacts",
        "sales_team",
    ],
    "license": 'AGPL-3',
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
