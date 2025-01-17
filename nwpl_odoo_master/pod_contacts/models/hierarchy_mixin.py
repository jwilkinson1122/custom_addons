# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.AbstractModel):
    _inherit = "res.partner"

    child_all_count = fields.Integer(
        'Indirect Affiliates Count',
        compute='_compute_affiliates', recursive=True, store=False,
        compute_sudo=True)
    child_count = fields.Integer(
        'Direct Affiliates Count',
        compute='_compute_child_count', recursive=True,
        compute_sudo=True,
    )

    def _get_affiliates(self, parents=None):
        if not parents:
            parents = self.env[self._name]

        indirect_affiliates = self.env[self._name]
        parents |= self
        direct_affiliates = self.child_ids - parents
        child_affiliates = direct_affiliates._get_affiliates(parents=parents) if direct_affiliates else self.browse()
        indirect_affiliates |= child_affiliates
        return indirect_affiliates | direct_affiliates

    @api.depends('child_ids', 'child_ids.child_all_count')
    def _compute_affiliates(self):
        for company in self:
            company.affiliate_ids = company._get_affiliates()
            company.child_all_count = len(company.affiliate_ids)

    @api.depends_context('uid', 'company')
    @api.depends('parent_id')
    def _compute_is_affiliate(self):
        affiliates = self.env.company_id.affiliate_ids
        if not affiliates:
            self.is_affiliate = False
        else:
            for company in self:
                company.is_affiliate = company in affiliates

    def _search_is_affiliate(self, operator, value):
        if operator not in ('=', '!=') or not isinstance(value, bool):
            raise UserError(_('Operation not supported'))
        # Double negation
        if not value:
            operator = '!=' if operator == '=' else '='
        if not self.env.company_id.affiliate_ids:
            return [('id', operator, self.env.company_id.id)]
        return (['!'] if operator == '!=' else []) + [('id', 'in', self.env.company_id.affiliate_ids.ids)]

    def _compute_child_count(self):
        company_read_group = self._read_group(
            [('parent_id', 'in', self.ids)],
            ['parent_id'],
            ['id:count'],
        )
        child_count_per_parent_id = dict(company_read_group)
        for company in self:
            company.child_count = child_count_per_parent_id.get(company._origin, 0)
