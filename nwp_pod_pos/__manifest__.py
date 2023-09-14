# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "NWP Podiatry link to PoS",
    "version": "15.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "depends": [
        "pos_session_pay_invoice",
        "nwp_pod_commission",
        "pos_inter_company",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_pod_center_company.xml",
        "views/product_template.xml",
        "views/pos_order.xml",
        "views/pos_payment.xml",
        "data/ir_sequence_data.xml",
        "wizard/wizard_pod_encounter_close_view.xml",
        "wizard/wizard_pod_encounter_finish_view.xml",
        "wizard/wizard_pod_encounter_add_amount_view.xml",
        "views/res_company_views.xml",
        "views/pod_encounter_views.xml",
        "views/pos_config_views.xml",
        "views/sale_order_views.xml",
        "views/pos_session_views.xml",
        "views/report_invoice.xml",
        "reports/report_pos_payment.xml",
    ],
    "website": "https://github.com/tegin/nwp-pod",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
