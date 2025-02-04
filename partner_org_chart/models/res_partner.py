# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class res_partner(models.Model):
    _inherit = ["res.partner"]

    affiliate_ids = fields.One2many('res.partner', string='Affiliates', compute='_compute_affiliates',
        help="Direct and indirect affiliates", compute_sudo=True)
    affiliate_all_count = fields.Integer('Indirect Affiliates Count',
        compute='_compute_affiliates', recursive=True, store=False, compute_sudo=True)

    def _get_affiliates(self, parents=None):
        if not parents:
            parents = self.env[self._name]

        indirect_affiliates = self.env[self._name]
        parents |= self
        direct_affiliates = self.affiliate_ids - parents
        child_affiliates = direct_affiliates._get_affiliates(parents=parents) if direct_affiliates else self.browse()
        indirect_affiliates |= child_affiliates
        return indirect_affiliates | direct_affiliates

    @api.depends('affiliate_ids', 'affiliate_ids.affiliate_all_count')
    def _compute_affiliates(self):
        for partner in self:
            partner.affiliate_ids = partner._get_affiliates()
            partner.affiliate_all_count = len(partner.affiliate_ids)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: