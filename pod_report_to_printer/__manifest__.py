{
    "name": "NWPL - Report to printer",
    "version": "17.0.0.0.0",
    "category": "Generic Modules/Base",
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "license": "LGPL-3",
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
            "/pod_report_to_printer/static/src/js/qweb_action_manager.esm.js",
        ],
    },
    "installable": True,
    "application": False,
    # "external_dependencies": {"python": ["pycups"]},
}
