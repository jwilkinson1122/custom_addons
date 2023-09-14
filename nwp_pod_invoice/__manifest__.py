

{
    "name": "NWP Podiatry Invoice",
    "version": "15.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "depends": [
        "pos_validation",
        "account_invoice_supplier_self_invoice",
        "account_move_change_company",
        "account_reconciliation_widget",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/pod_encounter_change_partner_views.xml",
        "views/pod_encounter_views.xml",
        "views/res_company_views.xml",
    ],
    "website": "https://github.com/tegin/nwp-pod",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
