# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Partner Entity',
    'summary': 'Partner Entity Module used by CLVsol Solutions.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'base',
        'contacts',
        'base_address_city',
        'base_address_extended',
        'clv_base',
        'clv_global_log',
    ],
    'data': [
        # 'views/base_address_extended.xml',
        'data/base_address_extended_data.xml',
        'views/res_partner_view.xml',
        'views/res_partner_log_view.xml',
        'views/abstract_partner_entity_view.xml',
        'views/base_address_city_menu_view.xml',
        'data/global_log_client.xml',
    ],
    'post_init_hook': '_update_street_format',
    'demo': [],
    'test': [],
    'init_xml': [],
    'test': [],
    'update_xml': [],
    'installable': True,
    'application': False,
    'active': False,
    'css': [],
}
