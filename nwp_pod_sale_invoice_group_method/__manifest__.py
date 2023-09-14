# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Sale Invoice Group Method",
    "version": "15.0.1.0.1",
    "author": "Eficent, CreuBlanca",
    "category": "Podiatry",
    "depends": [
        "pod_base",
        "nwp_pod_careplan_sale",
        "barcodes",
        "barcode_action",
        "pod_administration_encounter",
    ],
    "data": [
        "views/pod_authorization_method.xml",
        "data/pod_invoice_group.xml",
        "data/pod_preinvoice_group_sequence.xml",
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "views/pod_preinvoice_group_menu.xml",
        "views/report_invoice.xml",
        "wizard/wizard_sale_preinvoice_group_views.xml",
        "wizard/invoice_sales_by_group_view.xml",
        "views/pod_preinvoice_group_line_view.xml",
        "views/res_company_views.xml",
        "views/sale_order_view.xml",
        "views/pod_coverage_agreement_item_view.xml",
        "views/pod_preinvoice_group_views.xml",
        "report/pod_preinvoice_group.xml",
    ],
    "website": "https://github.com/tegin/nwp-pod",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
