# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Sale Commission Cancel",
    "version": "14.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "website": "https://github.com/tegin/cb-addons",
    "summary": "Creates inter company relations",
    "sequence": 30,
    "category": "Sale",
    "depends": ["sale_commission"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "wizard/account_invoice_agent_change_view.xml",
        "views/account_invoice_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
