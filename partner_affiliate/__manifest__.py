{
    "name": "Partner Affiliates",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "category": "Relationship Management",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base", 
        "contacts",
        "sale",
        "sale_management",
        "account",
        "account_accountant",
        "l10n_us",
        "stock",
        ],
    "data": [
        "security/ir.model.access.csv",
        "data/res_partner_type_data.xml",
        "views/res_partner_type_view.xml",
        "views/res_partner_view.xml",
        ],
}
