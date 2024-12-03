# -*- coding: utf-8 -*-

{
    "name": "Partner Organization",
    "version": "0.1",
    "depends": [
        "contacts",
        "sales_team",
    ],
    "license": "AGPL-3",
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
