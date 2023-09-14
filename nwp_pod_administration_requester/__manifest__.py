{
    "name": "NWP Podiatry Requester",
    "version": "15.0.1.0.0",
    "category": "NWP",
    "website": "https://github.com/tegin/nwp-pod",
    "author": "NWPL",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "NWP pod location data",
    "depends": [
        "pod_administration_practitioner",
        "pod_workflow",
        "pod_clinical_careplan",
    ],
    "data": [
        # "data/ir_sequence_data.xml",
        "security/security.xml",
        "views/res_partner_views.xml",
        "views/pod_menu.xml",
        "wizard/pod_careplan_add_plan_definition_views.xml",
    ],
}
