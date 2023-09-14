{
    "name": "Base Comments Templates",
    "summary": "Add conditional mako template to any report"
    "on models that inherits comment.template.",
    "version": "15.0.3.0.0",
    "category": "Reporting",
    "website": "https://nwpodiatric.com",
    "author": "NWPL",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "wizard/base_comment_template_preview_views.xml",
        "views/base_comment_template_view.xml",
        "views/res_partner_view.xml",
    ],
}
