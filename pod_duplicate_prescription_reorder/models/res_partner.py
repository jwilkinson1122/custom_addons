# -*- coding : utf-8 -*-


from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    prescription_order_ids = fields.One2many('prescription.order','partner_id',string='Prescription Orders')
    reorder_count = fields.Integer(compute='_compute_reorder_order_count', string='Reorder')

    def _compute_reorder_order_count(self):
        count = self.env['prescription.order'].search_count([('partner_id','=',self.id),('state','=','prescription'),('is_reorder','=',True)])
        self.reorder_count = count

    def open_prescription_from_view_action(self):
        action = self.env["ir.actions.actions"]._for_xml_id("pod_prescription.action_prescription")
        action['domain'] = [('partner_id','=',self.id),('state','=','prescription'),('is_reorder','=',True)]
        return action