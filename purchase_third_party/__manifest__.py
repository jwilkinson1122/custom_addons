# Copyright 2019 Creu Blanca
# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Purchase Third Party",
    "version": "14.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "website": "https://github.com/tegin/cb-addons",
    "summary": "Creates inter company relations",
    "sequence": 30,
    "category": "Sale",
    "depends": ["purchase_stock"],
    "license": "AGPL-3",
    "data": [
        "views/res_partner.xml",
        "report/external_layout.xml",
        "report/purchase_order_templates.xml",
        "report/purchase_quotation_templates.xml",
        "data/mail_template_data.xml",
        "views/purchase_order_views.xml",
        "views/product_supplierinfo_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
