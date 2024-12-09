# -*- coding: utf-8 -*-
{
    "name": "Customer Sequence",
    "license": "OPL-1",
    "category": "Sales",
    "version": "1.0",
    "depends": [

        "contacts",
    ],
    "application": True,
    "data": [
        'data/partner_seq_data.xml',
        'views/res_config_setting_view.xml',
        'views/res_partner_view.xml',
    ],

    "auto_install": False,
    "installable": True,
}
