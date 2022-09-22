# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-Today Geminate Consultancy Services (<http://geminatecs.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Contacts Hierarchy Chart",
    'summary': """It helps you to show all child contacts under parent contact which can be easily expanded and collapsed.""",
    'description': """Geminate comes with the features of the contacts hierarchy chart. it helps you to show all child contacts under parent contact which can be easily expanded and collapsed.
                        The benefit of this feature is, it provides a hierarchy of sub contacts under main contacts which draws organizational structure indirectly. you don't need to manually find subordinates or sub contacts of the main company.""",
    'author': "Geminate Consultancy Services",
    'website': "https://www.geminatecs.com",
    'version': '15.0.0.1',
    'category': 'Hierarchy Chart',
    'depends': ['sale'],
    'data': [
         'views/res_partner.xml',
         # 'views/template.xml',
         ],
    'assets': {
        'web.assets_backend': [
            'contacts_hierarchy_chart/static/src/js/partner_hierarchy.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'price': 39.99,
    'currency': 'EUR'
}
