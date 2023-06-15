# See LICENSE file for full copyright and licensing details.

{
    "name": "Podiatry Product Management",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry Management",
    "website": "http://www.nwpodiatric.com",
    "license": "AGPL-3",
    "summary": "A Module For Product Management For Podiatry",
    "depends": ["podiatry", "stock", "delivery", "purchase"],
    "data": [
        "data/library_sequence.xml",
        "data/library_category_data.xml",
        "data/library_card_schedular.xml",
        "security/library_security.xml",
        "security/ir.model.access.csv",
        'views/card_details.xml',
        "report/report_view.xml",
        "report/qrcode_label.xml",
        "views/library_view.xml",
        "wizard/terminate_reason.xml",
    ],
    "demo": ["demo/library_demo.xml"],
    "installable": True,
    "application": True,
}
