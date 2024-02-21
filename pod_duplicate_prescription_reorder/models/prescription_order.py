# -*- coding : utf-8 -*-


from odoo import api, fields, models, _

class Prescriptionorder(models.Model):
    _inherit = 'prescription.order'

    is_reorder = fields.Boolean('Is Reorder')

    def def_reorder_prescription(self):
        new_order = self.copy(default={
            'name': self.env['ir.sequence'].next_by_code('prescription.order') or 'New',
            'is_reorder': True,            
            'order_line': False,
        })
        for line in self.order_line:
            line.copy(default={
                'order_id': new_order.id,
            })
        return {
            'name': 'Reorder',
            'type': 'ir.actions.act_window',
            'res_model': 'prescription.order',
            'view_mode': 'form',
            'res_id': new_order.id,
            'target': 'new',
        }