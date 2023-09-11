{
    "name": "Report to printer remote",
    "version": "15.0.1.1.0",
    "category": "Generic Modules/Base",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "license": "AGPL-3",
    "depends": [
        "base_remote", 
        "base_report_to_printer"
        ],
    "data": [
        "views/printing_printer.xml",
        "data/printing_data.xml",
        "security/ir.model.access.csv",
        "views/res_remote_views.xml",
        "views/res_remote_printer_views.xml",
    ],
    "installable": True,
}
