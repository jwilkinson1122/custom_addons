from odoo import models, api
import json


class ProductFromPos(models.Model):
    _inherit = 'medical.prescription'

    @api.model
    def create_product_pos(self, vals):
        vals = json.loads(vals)
        vals["state"] = "Confirm"
        rec = self.env['medical.prescription'].create(vals)
        new_vals = self.env['podiatry.doctor'].search(
            [('id', '=', vals["doctor_id"])])
        vals["doctor_id"] = {}
        vals["doctor_id"][0] = new_vals.id
        vals["doctor_id"][1] = new_vals.name
        new_vals = self.env['eye.test.type'].search(
            [('id', '=', vals["test_type"])])
        vals["test_type"] = {}
        vals["test_type"][0] = new_vals.id
        vals["test_type"][1] = new_vals.name
        new_vals = self.env['res.partner'].search(
            [('id', '=', vals["customer"])])
        vals["customer"] = {}
        vals["customer"][0] = new_vals.id
        vals["customer"][1] = new_vals.name
        vals["id"] = rec.id
        return vals