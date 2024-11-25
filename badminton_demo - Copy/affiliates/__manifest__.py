# -*- coding: utf-8 -*-
{
    "name": "Affiliates",
    "category": "Sport",
    "version": "0.1",
    "depends": [
        "calendar",
        "practice",
        "project",
    ],
    "data": [
        "security/security.xml",
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "views/calendar_views.xml",
        "views/affiliate_views.xml",
        "views/affiliate_event_views.xml",
        "views/res_config_settings_views.xml",
        "wizards/affiliate_event_mail_wizard_views.xml",
        "actions/affiliate_actions.xml",
        "actions/affiliate_event_actions.xml",
        "views/menus.xml",
        "data/res_users_data.xml",
    ],
    "demo": [
        "data/demo/addreses_demo.xml",
        "data/demo/affiliate_demo.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
