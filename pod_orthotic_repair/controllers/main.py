# -*- coding: utf-8 -*-
import base64
from odoo import http, _
from odoo.http import request
from datetime import datetime, time
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


def validate_mandatory_fields(mandate_fields, kw):
    error, data = None, {}
    for key, value in mandate_fields.items():
        if not kw.get(key):
            error = "Mandatory fields " + value + " Missing"
            break
        else:
            data[key] = kw.get(key)
    return error, data


def validate_optional_fields(opt_fields, kw):
    data = {}
    for fld in opt_fields:
        if kw.get(fld):
            data[fld] = kw.get(fld)
    return data


class CreateRepairOrder(http.Controller):
    @http.route('/order/create', type='http', auth='user', website=True)
    def get_repair_web_form(self, **kw):
        order_data = request.env['orthotic.repair.order'].sudo().search([])
        customer_data = request.env['res.partner'].sudo().search([])
        orthotic_product = request.env['product.product'].sudo().search([('is_orthotic', '=', True)])
        customer_state = request.env['res.country.state'].sudo().search([])
        customer_country = request.env['res.country'].sudo().search([])
        values = {
            'order_data': order_data,  # many2one field
            'customer_data': customer_data,
            'orthotic_product': orthotic_product,
            'customer_state': customer_state,
            'customer_country': customer_country,
        }
        return request.render('pod_orthotic_repair.repair_request_order_page', values)

    @http.route('/get_country_wise_state', type='json', auth='public')
    def get_country_state(self, country_id):
        country_wise_state = {}
        if country_id:
            customer_state = request.env['res.country.state'].sudo().search([('country_id', '=', int(country_id))])
            for data in customer_state:
                country_wise_state[data.id] = data.name
        return country_wise_state

    @http.route('/create/repair-order', type='http', auth='user', website=True)
    def create_web_repair_order(self, **kw):
        order_data = request.env['orthotic.repair.order'].sudo().search([])
        customer_data = request.env['res.partner'].sudo().search([])
        orthotic_product = request.env['product.product'].sudo().search([('is_orthotic', '=', True)])
        customer_state = request.env['res.country.state'].sudo().search([])
        customer_country = request.env['res.country'].sudo().search([])
        values = {
            'order_data': order_data,  # many2one field
            'customer_data': customer_data,
            'orthotic_product': orthotic_product,
            'customer_state': customer_state,
            'customer_country': customer_country,
        }
        data = {}
        mandatory_fields = {'orthotic_problem': 'Orthotic Problem', 'orthotic_product_id': 'Orthotic'}

        optional_fields = ['model', 'orthotic_brand', 'mfg_year', 'serial_number', 'orthotic_product_id',
                           'is_previous_service_history', 'customer_id', 'phone', 'email', 'street', 'street2', 'city',
                           'zip', 'state_id', 'country_id', 'problem_description', 'file_name', 'avatar']

        error, orthotic_data = validate_mandatory_fields(mandatory_fields, kw)
        if error:
            values['error'] = error
            kw.update(values)
            return request.render('pod_orthotic_repair.repair_request_order_page', kw)

        if kw.get('document', False):
            img = kw.get('document')
            file_string = str(kw.get('document'))
            filename = file_string[file_string.index("'") + 1: file_string.index("'", file_string.index("'") + 1)]
            image = base64.b64encode(img.read())
            orthotic_data['attachment'] = image
            orthotic_data['file_name'] = filename

        opt_data = validate_optional_fields(optional_fields, kw)
        orthotic_data.update(opt_data)
        orthotic_data['customer_id'] = request.env.user.partner_id.id
        orthotic_data['phone'] = request.env.user.partner_id.phone
        orthotic_data['email'] = request.env.user.partner_id.email
        orthotic_data['is_website_order'] = True

        order_details = request.env['orthotic.repair.order'].sudo().create(orthotic_data)
        return request.render('pod_orthotic_repair.repair_order_created', {'order_details': order_details})

    @http.route('/order/repair-request-details', website=True, auth="public")
    def get_repair_request(self, **kw):
        order_request = request.env['orthotic.repair.order'].sudo().search(
            [('customer_id', '=', request.env.user.partner_id.id), ('is_website_order', '=', True)])
        return request.render('pod_orthotic_repair.repair_order_page', {
            'order_request': order_request
        })

    @http.route(['/order/request-information/<int:id>'], type='http', auth="user", website=True)
    def request_information_detail(self, id):
        orthotic_repair_id = request.env['orthotic.repair.order'].sudo().browse(id)
        if orthotic_repair_id.customer_id.id == request.env.user.partner_id.id:
            return request.render('pod_orthotic_repair.request_information_page', {
                'orthotic_repair_id': orthotic_repair_id
            })
        else:
            return request.redirect('/')


class CustomerRequestPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        count = request.env['orthotic.repair.order'].sudo().search_count(
            [('customer_id', '=', request.env.user.partner_id.id), ('is_website_order', '=', True)])
        values['count'] = count
        return values
