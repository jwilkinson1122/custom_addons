# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Coverage Request",
    "summary": "Podiatry financial coverage request",
    "version": "15.0.1.0.0",
    "author": "CreuBlanca, Eficent",
    "website": "https://github.com/tegin/nwp-pod",
    "license": "AGPL-3",
    "depends": [
        "pod_clinical_request_group",
        "pod_clinical_procedure",
        "pod_administration_encounter_careplan",
        "pod_document",
        "pod_clinical_laboratory",
        "pod_financial_coverage_agreement",
        "pod_encounter_identifier",
    ],
    "data": [
        "views/pod_authorization_web.xml",
        "data/pod_authorization_method_data.xml",
        "data/pod_authorization_format_data.xml",
        "security/ir.model.access.csv",
        "views/pod_authorization_method_view.xml",
        "wizard/pod_careplan_add_plan_definition_views.xml",
        "wizard/pod_request_group_change_plan_views.xml",
        "wizard/pod_request_group_check_authorization_views.xml",
        "views/res_partner_views.xml",
        "views/pod_request_views.xml",
        "views/pod_request_group_views.xml",
        "views/pod_coverage_agreement_item_view.xml",
        "views/pod_coverage_agreement_view.xml",
        "views/pod_coverage_template_view.xml",
        "views/pod_authorization_format_view.xml",
        "views/workflow_plan_definition.xml",
        "views/workflow_plan_definition_action.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
