

from odoo import api, fields, models


class MassCancelOrders(models.TransientModel):
    _name = 'prescription.mass.cancel.orders'
    _description = "Cancel multiple quotations"

    prescription_order_ids = fields.Many2many(
        string="Prescription orders to cancel",
        comodel_name='prescription.order',
        default=lambda self: self.env.context.get('active_ids'),
        relation='prescription_order_mass_cancel_wizard_rel',
    )
    prescription_orders_count = fields.Integer(compute='_compute_prescription_orders_count')
    has_confirmed_order = fields.Boolean(compute='_compute_has_confirmed_order')

    @api.depends('prescription_order_ids')
    def _compute_prescription_orders_count(self):
        for wizard in self:
            wizard.prescription_orders_count = len(wizard.prescription_order_ids)

    @api.depends('prescription_order_ids')
    def _compute_has_confirmed_order(self):
        for wizard in self:
            wizard.has_confirmed_order = bool(
                wizard.prescription_order_ids.filtered(lambda rx: rx.state in ['prescription', 'done'])
            )

    def action_mass_cancel(self):
        self.prescription_order_ids._action_cancel()
