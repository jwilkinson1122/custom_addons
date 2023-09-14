{
    "name": "Report to printer",
    "version": "15.0.1.1.0",
    "category": "Generic Modules/Base",
    "author": "NWPL"
    " LasLabs, Camptocamp, Odoo Community Association (OCA),"
    " Open for Small Business Ltd",
    "website": "https://nwpodiatric.com",
    "license": "AGPL-3",
    "depends": ["web"],
    "data": [
        "data/printing_data.xml",
        "security/security.xml",
        "views/printing_printer.xml",
        "views/printing_server.xml",
        "views/printing_job.xml",
        "views/printing_report.xml",
        "views/res_users.xml",
        "views/ir_actions_report.xml",
        "wizards/print_attachment_report.xml",
        "wizards/printing_printer_update_wizard_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/base_report_to_printer/static/src/js/qweb_action_manager.esm.js",
        ],
    },
    "installable": True,
    "application": False,
    # "external_dependencies": {"python": ["pycups"]},
}
