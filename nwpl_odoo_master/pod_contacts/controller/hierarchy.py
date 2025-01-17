# -*- coding: utf-8 -*-

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request


class HierarchyController(http.Controller):
    _managers_level = 5  # FP request

    def _check_affiliate(self, affiliate_id, **kw):
        if not affiliate_id:  # to check
            return None
        affiliate_id = int(affiliate_id)

        context = kw.get('context', request.env.context)
        if 'affiliate_ids' in context:
            cids = context['affiliate_ids']
        else:
            cids = [request.env.company.id]

        Affiliate = request.env['res.partner'].with_context(affiliate_ids=cids)
        # check and raise
        if not Affiliate.check_access_rights('read', raise_exception=False):
            return None
        try:
            Affiliate.browse(affiliate_id).check_access_rule('read')
        except AccessError:
            return None
        else:
            return Affiliate.browse(affiliate_id)

    def _prepare_affiliate_data(self, affiliate):
        company = affiliate.sudo().company_id
        return dict(
            id=affiliate.id,
            name=affiliate.name,
            link='/mail/view?model=%s&res_id=%s' % ('res.partner', affiliate.id,),
            company_id=company.id,
            name=company.name or '',
            direct_sub_count=len(affiliate.child_ids - affiliate),
            indirect_sub_count=affiliate.child_all_count,
        )

    @http.route('/get_redirect_model', type='json', auth='user')
    def get_redirect_model(self):
        if request.env['res.partner'].check_access_rights('read', raise_exception=False):
            return 'res.partner'

    @http.route('/get_hierarchy', type='json', auth='user')
    def get_hierarchy(self, affiliate_id, **kw):

        affiliate = self._check_affiliate(affiliate_id, **kw)
        if not affiliate:  # to check
            return {
                'managers': [],
                'children': [],
            }

        # compute affiliate data for org chart
        ancestors, current = request.env['res.partner'].sudo(), affiliate.sudo()
        while current.parent_id and len(ancestors) < self._managers_level+1 and current != current.parent_id:
            ancestors += current.parent_id
            current = current.parent_id

        values = dict(
            self=self._prepare_affiliate_data(affiliate),
            managers=[
                self._prepare_affiliate_data(ancestor)
                for idx, ancestor in enumerate(ancestors)
                if idx < self._managers_level
            ],
            managers_more=len(ancestors) > self._managers_level,
            children=[self._prepare_affiliate_data(child) for child in affiliate.child_ids if child != affiliate],
        )
        values['managers'].reverse()
        return values

    @http.route('/hr/get_subordinates', type='json', auth='user')
    def get_subordinates(self, affiliate_id, subordinates_type=None, **kw):
        """
        Get affiliate subordinates.
        Possible values for 'subordinates_type':
            - 'indirect'
            - 'direct'
        """
        affiliate = self._check_affiliate(affiliate_id, **kw)
        if not affiliate:  # to check
            return {}

        if subordinates_type == 'direct':
            res = (affiliate.child_ids - affiliate).ids
        elif subordinates_type == 'indirect':
            res = (affiliate.subordinate_ids - affiliate.child_ids).ids
        else:
            res = affiliate.subordinate_ids.ids

        return res
