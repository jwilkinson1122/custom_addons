# -*- coding: utf-8 -*-
{
    "name": "NWPL - Partner Relation Hierarchy",
    "version": "17.0.0.0.0",
    "website": "https://www.nwpodiatric.com",
    "author": "NWPL",
    "category": "Contacts",
    "license": "AGPL-3",
    "depends": [
        "pod_partner_multi_relation",
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/res_partner_relation_type.xml',
    ],
    "auto_install": False,
    "installable": True,
}
