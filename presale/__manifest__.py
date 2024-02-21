# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "presale",
    "summary": "Track pre-sale related things",
    "description": "Pre-Sale management app",
    "category": "PresSale Management",
    "author": "Odoo PS",
    "depends": ["base", "sale", "product"],
    "website": "https://www.odoo.com",
    "license": "OEEL-1",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequences.xml",
        "data/cron_actions.xml",
        "data/email_templates.xml",
        "views/presale_order_line_views.xml",
        "views/presale_views.xml",
        "views/sale_order_views.xml",
        "views/presale_menus.xml",
    ],
    "installable": True,
    "application": True,
}
