# -*- coding: utf-8 -*-
{
    "name": "Integration - MS SQL to Odoo",
    "version": "17.0.1.0.3",
    "sequence": 1,
    "summary": """Integrate MS SQL data to Odoo""",
    "description": """"This module help to integrate data from MS SQL to odoo""",
    "category": "Extra Tools",
    "depends": ["base", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "views/sql_integration.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "pod_sql_integration/static/src/scss/customizations.scss",
        ],
    },
    "qweb": [],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": False,
    "external_dependencies": {
        "python": ["pyodbc"],
    },
}
