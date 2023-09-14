# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Careplan to sales",
    "version": "15.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "category": "Podiatry",
    "depends": [
        "sale_third_party",
        "pod_authorization",
        "nwp_sale_report_invoice",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/pod_invoice_group.xml",
        "data/pod_sub_payor_sequence.xml",
        "wizard/pod_careplan_add_plan_definition_views.xml",
        "wizard/pod_encounter_add_careplan.xml",
        "wizard/pod_request_group_discount_views.xml",
        "reports/sale_report_templates.xml",
        "views/account_invoice_views.xml",
        "views/nomenclature_menu.xml",
        "views/report_invoice.xml",
        "views/pod_request_group_view.xml",
        "views/pod_encounter_views.xml",
        "views/pod_request_views.xml",
        "views/pod_laboratory_event_view.xml",
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
        "views/pod_coverage_agreement_view.xml",
        "views/pod_authorization_method_view.xml",
        "views/sale_order_views.xml",
        "views/pod_sale_discount_views.xml",
        "views/theme_default_templates.xml",
    ],
    "website": "https://github.com/tegin/nwp-pod",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
