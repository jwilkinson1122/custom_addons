

from odoo import api, fields, models


class MassCancelOrders(models.TransientModel):
    _name = 'prescription.mass.cancel.orders'
    _description = "Cancel multiple quotations"

    prescription_ids = fields.Many2many(
        string="Prescription orders to cancel",
        comodel_name='prescription',
        default=lambda self: self.env.context.get('active_ids'),
        relation='prescription_mass_cancel_wizard_rel',
    )
    prescriptions_count = fields.Integer(compute='_compute_prescriptions_count')
    has_confirmed_order = fields.Boolean(compute='_compute_has_confirmed_order')

    @api.depends('prescription_ids')
    def _compute_prescriptions_count(self):
        for wizard in self:
            wizard.prescriptions_count = len(wizard.prescription_ids)

    @api.depends('prescription_ids')
    def _compute_has_confirmed_order(self):
        for wizard in self:
            wizard.has_confirmed_order = bool(
                wizard.prescription_ids.filtered(lambda so: so.state in ['prescription', 'done'])
            )

    def action_mass_cancel(self):
        self.prescription_ids._action_cancel()