# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Podiatry Turn Management",
    "summary": """
        Manage Profesional turn management""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/nwp-pod",
    "depends": [
        "pod_administration_practitioner",
        "web_view_calendar_list",
        "pod_base",
        "pod_administration_center",
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
