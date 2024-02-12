# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.addons.account.controllers import portal
from odoo.osv.expression import AND, OR

class BlanketSalesOrderPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'prescription_count_custom' in counters:
            values['prescription_count_custom'] = request.env['prescription'].search_count(self._get_custom_prescription_domain())
        return values

    def _prescription_get_page_view_values_custom(self, prescription_custom_id, access_token, **kwargs):
        page_name = 'prescription_page_custom'
        history = 'web_prescription_history'
        values = {
            'page_name': page_name,
            'prescription_custom_id':prescription_custom_id,
        }
        return self._get_page_view_values(prescription_custom_id, access_token, values, history, False, **kwargs)

    def _get_custom_prescription_domain(self):
        partner = request.env.user.partner_id
        return [('partner_id','child_of', partner.commercial_partner_id.id)]

    def _get_searchbar_sortings_bso_custom(self):
        return {
            'date': {'label': _('Newest'), 'order': 'date_order desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'status': {'label': _('Status'), 'order': 'state'}
        }

    def _get_searchbar_inputs_bso_custom(self):
        values = {
            'name': {'input': 'name', 'label': _('Search in Name'), 'order': 1},
        }
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_search_domain_bso_custom(self, search_in, search):
        search_domain = []   
        if search_in in ('name'):
            search_domain = OR([search_domain, [('name', 'ilike', search)]])
        if search_in in ('status'):
            search_domain = OR([search_domain, [('state', 'ilike', 'draft' if search == 'Quotation' else 'ongoing' if search == 'Ongoing' else 'done' if search == 'Closed' else 'cancel' if search == 'Cancelled' else search)]])  
        return search_domain    


    @http.route(['/web/portal/prescription_view', '/web/portal/prescription_view/page/<int:page>'], type='http', auth='user', website=True)
    def portal_prescription_details_custom(self, page=1, sortby=None, search=None, search_in='name', filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        prescription_custom_obj = request.env['prescription']
        domain = self._get_custom_prescription_domain()
        bso_custom_count = prescription_custom_obj.search_count(domain)
        searchbar_sortings = self._get_searchbar_sortings_bso_custom()
        searchbar_inputs = self._get_searchbar_inputs_bso_custom()
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'done': {'label': _('Closed'), 'domain': [('state', '=', 'done')]},
            'draft': {'label': _('Quotation'), 'domain': [('state', '=', 'draft')]},
            'ongoing': {'label': _('Ongoing'), 'domain': [('state', '=', 'ongoing')]},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if search and search_in:
            domain += self._get_search_domain_bso_custom(search_in, search)

        pager = portal_pager(
            url="/web/portal/prescription_view'",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby},
            total=bso_custom_count,
            page=page,
            step=self._items_per_page
        )
        total_bso_custom = prescription_custom_obj.search(domain, order=order,limit=self._items_per_page, offset=pager['offset'])
        request.session['web_prescription_history'] = total_bso_custom.ids[:100]
        values.update({
            'total_bso_custom': total_bso_custom,
            'page_name': 'prescription_page_custom',
            'default_url': '/web/portal/prescription_view',
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'pager': pager
        })
        return  request.render('prescription_portal.custom_prescription_details_page', values)

    @http.route(['/web/portal/prescription/view/<int:prescription_custom_id_id>'], type='http', auth="user", website=True)
    def _prescription_get_page_view_values_custom(self, prescription_custom_id_id, access_token=None, **kwargs):
        prescription_custom_id = request.env['prescription'].browse(prescription_custom_id_id)
        if request.env.user.partner_id.commercial_partner_id != prescription_custom_id.partner_id.commercial_partner_id:
            return request.redirect('/my')
        try:
            bso_sudo = self._document_check_access('prescription', prescription_custom_id_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._prescription_get_page_view_values_custom(bso_sudo, access_token, **kwargs)
        return request.render('prescription_portal.portal_prescription_custom_form',values)