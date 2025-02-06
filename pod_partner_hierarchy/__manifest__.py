# -*- coding: utf-8 -*-
{
    "name": "Partner Hierarchies",
    "version": "0.1",
    "depends": [
        "base",
        "base_setup",
        # "account",
        # "mail",
        # "web",
        # "web_hierarchy",
        # "pod_web_chatter",
        "contacts",
    ],
    "license": "AGPL-3",
    "sequence": 0,
    "data": [
        "security/ir.model.access.csv",
        "data/res_partner_type_data.xml",
        "data/res_partner_company_type_data.xml",
        "data/ir_sequence_data.xml",
        "views/res_partner_view.xml",
        "views/res_partner_type_view.xml",
        "views/res_partner_company_type_view.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            # "pod_partner_hierarchy/static/src/scss/variables.scss",
        ],
        "web.assets_backend": [
            # "pod_partner_hierarchy/static/src/fields/*",
            # "pod_partner_hierarchy/static/src/views/**/*",
        ],
    },
    "demo": [],
    "auto_install": False,
    "installable": True,
    "application": False,
}
