{
    "name": "Podiatry Block Requests",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "depends": [
        "pod_administration_encounter",
        "pod_workflow",
        # "pod_workflow",
        # "pod_clinical_careplan",
        
        # pod_encounter_identifier
        #  "pod_clinical_request_group",
        # "sale_commission_delegated_partner",
        # "pod_sale_invoice_group_method",
        # "pod_workflow_activity",
        # "pod_clinical_procedure"
        #       "pod_workflow",
        # "pod_administration_location",
        ],
    # "depends": ["nw_pod_pos"],
    "data": [
        "views/pod_request_views.xml",
        "views/workflow_plan_definition_action.xml",
    ],
    "website": "https://nwpodiatric.com",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
