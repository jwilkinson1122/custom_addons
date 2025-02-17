# -*- coding: utf-8 -*-
{
    "name": "Partner Hierarchies",
    "version": "0.1",
    "depends": [
        "base",
        # "base_setup",
        # "account",
        "web",
        "mail",
        "web_hierarchy",
        "contacts",
        "pod_web_chatter",
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
            "nwpl_odoo_master/static/src/scss/variables.scss",
        ],
        "web.assets_backend": [
            "nwpl_odoo_master/static/src/fields/*",
            "nwpl_odoo_master/static/src/views/**/*",
        ],
    },
    "demo": [],
    "auto_install": False,
    "installable": True,
    "application": False,
}
