# -*- coding: utf-8 -*-

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request


class ContactOrgChartController(http.Controller):
    _managers_level = 5  # FP request

    def _check_partner(self, partner_id, **kw):
        if not partner_id:  # to check
            return None
        partner_id = int(partner_id)

        context = kw.get('context', request.env.context)
        if 'allowed_company_ids' in context:
            cids = context['allowed_company_ids']
        else:
            cids = [request.env.company.id]

        Partner = request.env['res.partner'].with_context(allowed_company_ids=cids)
        if not Partner.check_access_rights('read', raise_exception=False):
            return None
        try:
            Partner.browse(partner_id).check_access_rule('read')
        except AccessError:
            return None
        else:
            return Partner.browse(partner_id)

    def _prepare_partner_data(self, partner):
        return dict(
            id=partner.id,
            name=partner.name,
            phone=partner.phone,
            email=partner.email,
            link='/mail/view?model=%s&res_id=%s' % ('res.partner', partner.id,),
            direct_sub_count=len(partner.child_ids - partner),
            indirect_sub_count=partner.affiliates_count,
        )

    @http.route('/partner/get_redirect_model', type='json', auth='user')
    def get_redirect_model(self):
        return 'res.partner'
#         if request.env['res.partner'].has_access('read'):
#             return 'res.partner'
#         return 'res.partner'

    # @http.route('/partner/get_org_chart', type='json', auth='user')
    # def get_org_chart(self, partner_id, **kw):

    #     partner = self._check_partner(partner_id, **kw)
    #     if not partner: 
    #         return {
    #             'managers': [],
    #             'children': [],
    #         }

    #     ancestors, current = request.env['res.partner'].sudo(), partner.sudo()
    #     while current.parent_id and len(ancestors) < self._managers_level + 1 and current != current.parent_id:
    #         ancestors += current.parent_id
    #         current = current.parent_id

    #     values = dict(
    #         self=self._prepare_partner_data(partner),
    #         managers=[
    #             self._prepare_partner_data(ancestor)
    #             for idx, ancestor in enumerate(ancestors)
    #             if idx < self._managers_level
    #         ],
    #         managers_more=len(ancestors) > self._managers_level,
    #         children=[self._prepare_partner_data(child) for child in partner.child_ids if child != partner],
    #     )
    #     values['managers'].reverse()
    #     return values

    @http.route('/partner/get_org_chart', type='json', auth='user')
    def get_org_chart(self, partner_id, include_contacts=False, **kw):
        partner = self._check_partner(partner_id, **kw)
        if not partner:
            # Return an empty response if the partner doesn't exist or access is restricted
            return {
                'managers': [],
                'children': [],
                'contacts': [],
            }

        # Compute the manager hierarchy (ancestors)
        ancestors, current = request.env['res.partner'].sudo(), partner.sudo()
        while current.parent_id and len(ancestors) < self._managers_level + 1 and current != current.parent_id:
            ancestors += current.parent_id
            current = current.parent_id

        # Prepare the response data
        values = dict(
            self=self._prepare_partner_data(partner),
            managers=[
                self._prepare_partner_data(ancestor)
                for idx, ancestor in enumerate(ancestors)
                if idx < self._managers_level
            ],
            managers_more=len(ancestors) > self._managers_level,
            children=[
                self._prepare_partner_data(child)
                for child in partner.child_ids if child != partner
            ],
        )

        # Optionally include contacts if requested
        if include_contacts:
            values["contacts"] = [
                self._prepare_partner_data(contact)
                for contact in partner.child_ids
                # for contact in partner.contact_ids
            ]

        # Reverse the order of managers for proper hierarchy display
        values['managers'].reverse()

        return values





    @http.route('/partner/get_affiliates', type='json', auth='user')
    def get_affiliates(self, partner_id, affiliates_type=None, **kw):
        """
        Get partner affiliates.
        Possible values for 'affiliates_type':
            - 'indirect'
            - 'direct'
        """
        partner = self._check_partner(partner_id, **kw)
        if not partner:  # to check
            return {}

        if affiliates_type == 'direct':
            res = (partner.child_ids - partner).ids
        elif affiliates_type == 'indirect':
            res = (partner.affiliate_ids - partner.child_ids).ids
        else:
            res = partner.affiliate_ids.ids
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: