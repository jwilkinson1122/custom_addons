{
    "name": "Intercompany journal",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "summary": "Creates inter company relations",
    "sequence": 30,
    "category": "Accounting",
    "depends": ["account"],
    "external_dependencies": {
        "deb": ["zip"],
    },
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "views/res_inter_company_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
