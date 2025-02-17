# -*- coding: utf-8 -*-

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request


class PartnerHierarchyController(http.Controller):
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
            direct_sub_count=len(partner.affiliate_ids - partner),
            indirect_sub_count=partner.affiliates_count,
        )

    @http.route('/partner/get_redirect_model', type='json', auth='user')
    def get_redirect_model(self):
        return 'res.partner'

    # @http.route('/partner/get_partner_hierarchy', type='json', auth='user')
    # def get_partner_hierarchy(self, partner_id, **kw):

    #     partner = self._check_partner(partner_id, **kw)
    #     if not partner:  
    #         return {
    #             'managers': [],
    #             'affiliates': [],
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
    #         affiliates=[self._prepare_partner_data(affiliate) for affiliate in partner.affiliate_ids if affiliate != partner],
    #         children=[self._prepare_partner_data(child) for child in partner.child_ids if child != partner],

    #     )
    #     values['managers'].reverse()
    #     return values

    @http.route('/partner/get_partner_hierarchy', type='json', auth='user')
    def get_partner_hierarchy(self, partner_id, **kw):

        partner = self._check_partner(partner_id, **kw)
        if not partner:
            return {
                'managers': [],
                'affiliates': [],
                'children': [],
            }

        # Ensure hierarchy starts from the viewed partner
        ancestors, current = request.env['res.partner'].sudo(), partner.sudo()
        while current.parent_id and len(ancestors) < self._managers_level + 1 and current != current.parent_id:
            ancestors += current.parent_id
            current = current.parent_id

        values = dict(
            self=self._prepare_partner_data(partner),
            managers=[self._prepare_partner_data(ancestor) for idx, ancestor in enumerate(ancestors) if idx < self._managers_level],
            managers_more=len(ancestors) > self._managers_level,
            affiliates=[self._prepare_partner_data(affiliate) for affiliate in partner.affiliate_ids],
            children=[self._prepare_partner_data(child) for child in partner.sub_affiliate_ids],
        )
        values['managers'].reverse()
        return values



    # Affiliates
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
            res = (partner.affiliate_ids - partner).ids
        elif affiliates_type == 'indirect':
            res = (partner.affiliate_ids - partner.affiliate_ids).ids
        else:
            res = partner.affiliate_ids.ids
        return res
    
    # Contacts
    @http.route('/partner/get_children', type='json', auth='user')
    def get_children(self, partner_id, children_type=None, **kw):
        """
        Get partner contacts.
        Possible values for 'children_type':
            - 'indirect'
            - 'direct'
        """
        partner = self._check_partner(partner_id, **kw)
        if not partner:  # to check
            return {}

        if children_type == 'direct':
            res = (partner.child_ids - partner).ids
        elif children_type == 'indirect':
            res = (partner.child_ids - partner.child_ids).ids
        else:
            res = partner.child_ids.ids
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: