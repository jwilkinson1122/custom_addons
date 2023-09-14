# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Cancel",
    "version": "15.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "category": "Podiatry",
    "depends": ["nwp_pod_pos"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/pod_request_cancel_views.xml",
        "wizard/pod_careplan_cancel_views.xml",
        "wizard/pod_laboratory_request_cancel_views.xml",
        "wizard/pod_procedure_request_cancel_views.xml",
        "wizard/pod_request_group_cancel_views.xml",
        "wizard/pod_encounter_cancel_views.xml",
        "views/pod_sale_discount_views.xml",
        "views/pod_request_views.xml",
        "views/pod_careplan_view.xml",
        "views/pod_laboratory_request_view.xml",
        "views/pod_procedure_request_view.xml",
        "views/pod_request_group_view.xml",
        "views/pod_encounter_view.xml",
    ],
    "website": "https://github.com/tegin/nwp-pod",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
