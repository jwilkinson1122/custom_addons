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
        "pod_web_chatter",
        "contacts",
        "sales_team",
    ],
    "license": "AGPL-3",
    "sequence": 0,
    "data": [
        "security/ir.model.access.csv",
        # "views/kanban_template_view.xml",
        "views/res_partner_view.xml",
        "views/res_partner_type_view.xml",
        "data/res_partner_type_data.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            "pod_partner_hierarchy/static/src/scss/variables.scss",
        ],
        "web.assets_backend": [
            "pod_partner_hierarchy/static/src/fields/*",
            "pod_partner_hierarchy/static/src/views/**/*",
        ],
    },
    "demo": [],
    "auto_install": False,
    "installable": True,
    "application": False,
    # "pre_init_hook": "module_install_hook"
}
