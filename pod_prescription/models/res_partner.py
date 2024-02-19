# -*- coding: utf-8 -*-


from odoo import api, fields, models
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.osv import expression

class ResPartner(models.Model):
    _inherit = 'res.partner'

    prescription_order_count = fields.Integer(compute='_compute_prescription_order_count', string='Prescription Order Count')
    prescription_order_ids = fields.One2many('prescription.order', 'partner_id', 'Prescription Order')
    prescription_warn = fields.Selection(WARNING_MESSAGE, 'Prescription Warnings', default='no-message', help=WARNING_HELP)
    prescription_warn_msg = fields.Text('Message for Prescription Order')

    @api.model
    def _get_prescription_order_domain_count(self):
        return []

    def _compute_prescription_order_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search_fetch(
            [('id', 'child_of', self.ids)],
            ['parent_id'],
        )
        prescription_order_groups = self.env['prescription.order']._read_group(
            domain=expression.AND([self._get_prescription_order_domain_count(), [('partner_id', 'in', all_partners.ids)]]),
            groupby=['partner_id'], aggregates=['__count']
        )
        self_ids = set(self._ids)

        self.prescription_order_count = 0
        for partner, count in prescription_order_groups:
            while partner:
                if partner.id in self_ids:
                    partner.prescription_order_count += count
                partner = partner.parent_id

    def _has_order(self, partner_domain):
        self.ensure_one()
        prescription_order = self.env['prescription.order'].sudo().search(
            expression.AND([
                partner_domain,
                [
                    ('state', 'in', ('sent', 'prescription')),
                ]
            ]),
            limit=1,
        )
        return bool(prescription_order)

    def _can_edit_name(self):
        """ Can't edit `name` if there is (non draft) issued RX. """
        return super()._can_edit_name() and not self._has_order(
            [
                ('partner_invoice_id', '=', self.id),
                ('partner_id', '=', self.id),
            ]
        )

    def can_edit_vat(self):
        """ Can't edit `vat` if there is (non draft) issued RX. """
        return super().can_edit_vat() and not self._has_order(
            [('partner_id', 'child_of', self.commercial_partner_id.id)]
        )

    def action_view_prescription_order(self):
        action = self.env['ir.actions.act_window']._for_xml_id('pod_prescription.act_res_partner_2_prescription_order')
        all_child = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        action["domain"] = [("partner_id", "in", all_child.ids)]
        return action

    def _compute_credit_to_invoice(self):
        # EXTENDS 'account'
        super()._compute_credit_to_invoice()
        domain = [('partner_id', 'in', self.ids), ('state', '=', 'prescription')]
        group = self.env['prescription.order']._read_group(domain, ['partner_id'], ['amount_to_invoice:sum'])
        for partner, amount_to_invoice_sum in group:
            partner.credit_to_invoice += amount_to_invoice_sum


    def unlink(self):
        # Unlink draft/cancelled RX so that the partner can be removed from database
        self.env['prescription.order'].sudo().search([
            ('state', 'in', ['draft', 'cancel']),
            '|', '|',
            ('partner_id', 'in', self.ids),
            ('partner_invoice_id', 'in', self.ids),
            ('partner_shipping_id', 'in', self.ids),
        ]).unlink()
        return super().unlink()