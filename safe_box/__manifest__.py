

{
    "name": "Cash Box management",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "summary": "Creates inter company relations",
    "sequence": 30,
    "category": "Accounting",
    "depends": ["account"],
    "license": "AGPL-3",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "wizard/wizard_safe_box_move.xml",
        "wizard/wizard_safe_box_count.xml",
        "wizard/wizard_safe_box_move_external.xml",
        "views/safe_box_menu.xml",
        "views/safe_box_move_views.xml",
        "views/safe_box_group_views.xml",
        "views/safe_box_views.xml",
        "views/safe_box_coin_views.xml",
        "views/account_account_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
