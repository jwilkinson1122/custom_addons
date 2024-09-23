from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from odoo import http, _
from odoo.http import request
from odoo import api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import UserError


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

