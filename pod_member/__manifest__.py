{
    "name": "Podiatry Members",
    "description": "Manage members borrowing items.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": ["pod_app", "mail"],
    "application": False,
    "data": [
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "views/item_view.xml",
        "views/member_view.xml",
        "views/pod_menu.xml",
        "views/item_list_template.xml",
    ],
}
