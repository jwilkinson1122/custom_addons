# -*- coding: utf-8 -*-
{
    "name": "NW Podiatric Profile",
    "version": "0.1",
    "depends": [
        "practice_account",
        "affiliates",
        "contacts",
        "website_event",
    ],
    "data": [
        "views/templates/website_footer.xml",
        "views/templates/website_homepage.xml",
        "views/templates/website_membership_information.xml",
        "views/templates/website_practical_information.xml",
        "views/menus.xml",
        "data/mail_template_data.xml",
        "data/partner_data.xml",
        "data/website_data.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "profile_nwpodiatric/static/scss/website.scss",
        ],
    },
    "qweb": [],
    "installable": True,
    "application": False,
    "post_init_hook": "post_init_hook",
    "license": "LGPL-3",
}
