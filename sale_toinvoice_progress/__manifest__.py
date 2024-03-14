# -*- coding: utf-8 -*-
# Copyright© 2016-2017 ICTSTUDIO <http://www.ictstudio.eu>
# License: AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    'name': 'Sale Order To Invoice Progress',
    'version': '17.0.0.0.0',
    'category': 'Sale Management',
    'author': 'ICTSTUDIO | André Schenkels',
    'website': 'http://www.ictstudio.eu',
    'license': 'LGPL-3',
    'summary': 'Provide Progress bar for to invoice orders',
    'depends': [
        'sale'
    ],
    'data': [
        'views/sale_order.xml',
    ],
    'installable': True,
}