from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # def action_open_prescription_order(self):
    #     tree_id = self.env.ref("prescription.prescription_order_kpis_tree").id
    #     form_id = self.env.ref("prescription.prescription_order_form").id
    #     return {
    #         "name": _("Requests for Quotation"),
    #         "view_mode": "tree,form",
    #         'views': [(tree_id, 'tree'),(form_id,'form')],
    #         "res_model": "prescription.order",
    #         "domain":[('origin', '=', self.name)],
    #         "type": "ir.actions.act_window",
    #         "target": "current",
    #     }

    # def _get_po(self):

    #     for orders in self:
    #         prescription_ids = self.env['prescription.order'].sudo().search([('origin', '=', self.name)])
    #     orders.po_count = len(prescription_ids)

    # po_count = fields.Integer(compute='_get_po', string='Purchase Order')
