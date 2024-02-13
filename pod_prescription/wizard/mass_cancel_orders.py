

from odoo import api, fields, models


class MassCancelOrders(models.TransientModel):
    _name = 'prescriptions.mass.cancel.orders'
    _description = "Cancel multiple quotations"

    prescriptions_order_ids = fields.Many2many(
        string="Prescription orders to cancel",
        comodel_name='prescriptions.order',
        default=lambda self: self.env.context.get('active_ids'),
        relation='prescriptions_order_mass_cancel_wizard_rel',
    )
    prescriptions_orders_count = fields.Integer(compute='_compute_prescriptions_orders_count')
    has_confirmed_order = fields.Boolean(compute='_compute_has_confirmed_order')

    @api.depends('prescriptions_order_ids')
    def _compute_prescriptions_orders_count(self):
        for wizard in self:
            wizard.prescriptions_orders_count = len(wizard.prescriptions_order_ids)

    @api.depends('prescriptions_order_ids')
    def _compute_has_confirmed_order(self):
        for wizard in self:
            wizard.has_confirmed_order = bool(
                wizard.prescriptions_order_ids.filtered(lambda so: so.state in ['prescriptions', 'done'])
            )

    def action_mass_cancel(self):
        self.prescriptions_order_ids._action_cancel()
