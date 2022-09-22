# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import http
from odoo.http import request
from odoo import api, fields, models, SUPERUSER_ID, tools

class CustomerHierarchy(http.Controller):
    
    @http.route('/check/child', auth='public' , type='json' , website=True)
    def check_child(self,**kw):
        if 'id' in kw:
            if kw['id']:
                partner_id = request.env['res.partner'].sudo().search([('id','=',kw['id'])])
                ids = partner_id.child_ids.ids
                if len(partner_id.child_ids.ids) > 0:
                    return True
        return False

    @http.route('/customer/hierarchy', auth='public' , type='json' , website=True)
    def customer_hierarchy(self,**kw):
        if 'id' in kw:
            if kw['id']:
                partner_id = request.env['res.partner'].sudo().search([('id','=',kw['id'])])
                ids = partner_id.child_ids.ids
            return ids
        return False
