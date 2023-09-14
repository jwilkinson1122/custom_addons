# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Sale third party invoice",
    "version": "14.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "website": "https://github.com/tegin/cb-addons",
    "summary": "Creates inter company relations",
    "sequence": 30,
    "category": "Sale",
    "depends": ["sale"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "wizard/cash_third_party_sale_view.xml",
        "reports/sale_third_party_report_templates.xml",
        "reports/sale_third_party_report.xml",
        "views/sale_order_views.xml",
        "views/res_company_views.xml",
        "views/partner_views.xml",
        "views/account_payment_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
