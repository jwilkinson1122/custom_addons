# Copyright (C) 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "NWP Podiatry Guard",
    "version": "15.0.1.0.0",
    "category": "NWP",
    "website": "https://github.com/tegin/nwp-pod",
    "author": "CreuBlanca, Eficent",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "NWP pod location data",
    "depends": ["nwp_pod_commission"],
    "data": [
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/pod_menu.xml",
        "wizard/pod_guard_invoice_views.xml",
        "wizard/pod_guard_plan_apply_views.xml",
        "views/pod_guard_views.xml",
        "views/pod_guard_plan_views.xml",
        "views/res_partner_views.xml",
        "views/account_move_views.xml",
    ],
}
