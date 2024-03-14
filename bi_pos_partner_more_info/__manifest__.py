# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Customer Custom Fields/Extra Fields',
    'version': '17.0.0.0.0',
    'category': 'Point of Sales',
    'summary': 'POS customer extra details pos customer extra fields pos customer extra information pos contact extra details pos extra fields pos partner extra field point of sales extra fields point of sales customer extra information pos customer extra details on pos',
    'description': """

        POS Partner More Information in odoo,
        POS Contact Additional Info in odoo,
        Configure Custom Partner Information in odoo,
        Select Custom Field in odoo,
        Create Custom Field in odoo,
        Add Additional Information of Partner in odoo,
        Additional Information in More Info tab in odoo,    
    
    """,
    'author': 'BrowseInfo',
    "price": 35,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.com',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        # 'views/assets.xml',
        'views/res_partner_view.xml',
        'views/pos_config_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            "bi_pos_partner_more_info/static/src/js/Screens/ClientListScreen/ClientDetailsEdit.js",
            "bi_pos_partner_more_info/static/src/js/Screens/ClientListScreen/ClientListScreen.js",
            "bi_pos_partner_more_info/static/src/js/models.js",

        ],
        'web.assets_qweb': [
            'bi_pos_partner_more_info/static/src/xml/**/*',
        ],
    },
    
    'license': 'OPL-1',
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/0IpQy9Dh0t0',
    "images": ['static/description/Banner.png'],
}

