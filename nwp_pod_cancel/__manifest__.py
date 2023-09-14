

{
    "name": "Podiatry Cancel",
    "version": "15.0.1.0.0",
    "author": "NWPL",
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
    "website": "https://nwpodiatric.com",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
