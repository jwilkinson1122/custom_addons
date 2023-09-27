

{
    "name": "Podiatry Turn Management",
    "summary": """
        Manage Profesional turn management""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": [
        "pod_base",
        "web_view_calendar_list",
        "pod_base",
        "pod_base",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/pod_menu.xml",
        "wizards/wzd_pod_turn.xml",
        "views/res_partner.xml",
        "views/pod_turn_specialty.xml",
        "views/pod_turn.xml",
        "views/pod_turn_tag.xml",
    ],
}
