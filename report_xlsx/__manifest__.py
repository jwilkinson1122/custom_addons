{
    "name": "Base report xlsx",
    "summary": "Base module to create xlsx report",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "category": "Reporting",
    "version": "15.0.1.1.3",
    "license": "AGPL-3",
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "depends": ["base", "web"],
    "demo": ["demo/report.xml"],
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "report_xlsx/static/src/js/report/action_manager_report.esm.js",
        ],
    },
}
