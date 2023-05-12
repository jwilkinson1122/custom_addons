# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PosOrder(models.Model):
	_inherit = 'pos.order'

	pod_reference = fields.Many2one('practitioner.prescription', string='Podiatry Reference')

	@api.model
	def _order_fields(self, ui_order):
		res = super(PosOrder, self)._order_fields(ui_order)
		res.update({'pod_reference': ui_order.get('pod_reference')})
		return res
