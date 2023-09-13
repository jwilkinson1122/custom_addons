{
    "name": "Barcode action launcher",
    "version": "15.0.1.0.0",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "author": "NWPL",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Allows to use barcodes as a launcher",
    "depends": ["barcodes"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/barcode_action_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "barcode_action/static/src/js/action_barcode_form.js",
            "barcode_action/static/src/js/action_barcode_widget.js",
        ],
    },
    "demo": ["demo/barcode_action_demo.xml"],
}
