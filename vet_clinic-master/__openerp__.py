# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2016 Didotech srl (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# #############################################################################

{
    'name': 'Veterinary Clinic',
    'version': '4.0.0.0',
    'category': 'Generic Modules/Service',
    'author': 'Andrei Levin - Didotech Srl',
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/clinic_view.xml',
        'views/partner_view.xml',
        'reports/paper_format.xml',
        'reports/report_saleorder.xml'
    ],
    'test': [],
    'installable': True,
    'active': False,
}
