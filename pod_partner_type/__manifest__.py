# -*- coding: utf-8 -*-
{
    "name": "QS CRM and Partner Customization",
    "category": "Customizations",
    "version": "1.0",
    # any module necessary for this one to work correctly
    "depends": ["base", "contacts", "purchase", "project"],
    # always loaded
    "data": [
        # "security/security.xml",
        # "security/ir.model.access.csv",
        "data/res_partner_sequence.xml",
        "views/views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # "pod_partner_type/static/src/js/DisallowFilterForField.js"
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
