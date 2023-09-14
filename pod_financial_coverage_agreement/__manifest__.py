# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Financial Coverage Agreement",
    "version": "15.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "category": "Podiatry",
    "depends": [
        "pod_financial_coverage",
        "pod_administration_center",
        "pod_workflow",
        "product_nomenclature",
        "report_xlsx",
        "report_context",
    ],
    "website": "https://github.com/tegin/nwp-pod",
    "external_dependencies": {"python": ["pandas", "openpyxl"]},
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "wizards/pod_agreement_expand.xml",
        "wizards/pod_coverage_agreement_join.xml",
        "reports/items_export_xslx.xml",
        "reports/agreement_report.xml",
        "reports/agreement_compare_report.xml",
        "reports/pod_coverage_agreement_xlsx.xml",
        "reports/pod_coverage_agreement_xlsx_private.xml",
        "data/pod_coverage_agreement.xml",
        "wizards/pod_coverage_agreement_template_views.xml",
        "wizards/pod_agreement_change_prices_views.xml",
        "views/pod_coverage_agreement_item_view.xml",
        "views/pod_coverage_agreement_view.xml",
        "views/pod_coverage_template_view.xml",
        "views/pod_menu.xml",
        "views/product_views.xml",
        "views/workflow_plan_definition_views.xml",
        "views/product_category_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
