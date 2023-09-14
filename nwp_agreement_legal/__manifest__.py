# Copyright 2017 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Agreements Legal Demo",
    "summary": "Create contract from agreement",
    "author": "CreuBlanca, Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/nwp-addons",
    "category": "Agreement",
    "depends": ["agreement_legal", "archive_management"],
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "data": [
        "data/agreement_demo_data.xml",
        "views/agreement.xml",
        # "templates/assets.xml",
        "reports/agreement.xml",
    ],
    'assets': {
        'web.assets_frontend': [
        ],
        'web.report_assets_common': [
            'nwp_agreement_legal/static/src/scss/agreement_layout.scss',
        ],
    },
    "installable": True,
    "auto_install": False,
}
