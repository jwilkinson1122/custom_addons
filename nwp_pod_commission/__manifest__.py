

{
    "name": "Podiatry Commission",
    "summary": "Add Commissions",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "depends": [
        "sale_commission_formula",
        "sale_commission_cancel",
        "sale_commission_delegated_partner",
        "nwp_pod_sale_invoice_group_method",
        "nwp_pod_workflow_activity",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sale_commission_formula.xml",
        "views/account_invoice_view.xml",
        "views/res_partner_views.xml",
        "views/product_template_view.xml",
        "views/pod_laboratory_event_view.xml",
        "views/pod_procedure_request_view.xml",
        "views/pod_procedure_view.xml",
        "views/workflow_plan_definition_action.xml",
        "views/pod_encounter_views.xml",
        "views/pod_practitioner_condition_views.xml",
        "wizard/wizard_settle.xml",
    ],
    "website": "https://github.com/tegin/nwp-pod",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
