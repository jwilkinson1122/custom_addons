from odoo import models, api
import json


class ProductFromPos(models.Model):
    _inherit = 'podiatry.prescription'

    @api.model
    def create_product_pos(self, vals):
        vals = json.loads(vals)
        vals["state"] = "Confirm"
        rec = self.env['podiatry.prescription'].create(vals)
        new_vals = self.env['podiatry.practitioner'].search(
            [('id', '=', vals["practitioner_id"])])
        vals["practitioner_id"] = {}
        vals["practitioner_id"][0] = new_vals.id
        vals["practitioner_id"][1] = new_vals.name
        new_vals = self.env['orthotic.device.type'].search(
            [('id', '=', vals["device_type"])])
        vals["device_type"] = {}
        vals["device_type"][0] = new_vals.id
        vals["device_type"][1] = new_vals.name
        new_vals = self.env['res.partner'].search(
            [('id', '=', vals["customer"])])
        vals["customer"] = {}
        vals["customer"][0] = new_vals.id
        vals["customer"][1] = new_vals.name
        vals["id"] = rec.id
        return vals
