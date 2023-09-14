

{
    "name": "Sale Commission Cancel",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "summary": "Creates inter company relations",
    "sequence": 30,
    "category": "Sale",
    "depends": ["sale_commission"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "wizard/account_invoice_agent_change_view.xml",
        "views/account_invoice_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
