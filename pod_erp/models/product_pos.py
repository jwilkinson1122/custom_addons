from odoo import models, api
import json

class ProductFromPos(models.Model):
    _inherit = 'practitioner.prescription'

    @api.model
    def create_product_pos(self, vals):
        vals = json.loads(vals)
        vals["state"] = "Confirm"
        rec = self.env['practitioner.prescription'].create(vals)
        new_vals = self.env['podiatry.practitioner'].search([('id', '=', vals["practitioner"])])
        vals["practitioner"] = {}
        vals["practitioner"][0] = new_vals.id
        vals["practitioner"][1] = new_vals.name
        new_vals = self.env['eye.test.type'].search([('id', '=', vals["test_type"])])
        vals["test_type"] = {}
        vals["test_type"][0] = new_vals.id
        vals["test_type"][1] = new_vals.name
        new_vals = self.env['device.type'].search([('id', '=', vals["device_type"])])
        vals["device_type"] = {}
        vals["device_type"][0] = new_vals.id
        vals["device_type"][1] = new_vals.name
        new_vals = self.env['res.partner'].search([('id', '=', vals["patient"])])
        vals["patient"] = {}
        vals["patient"][0] = new_vals.id
        vals["patient"][1] = new_vals.name
        vals["id"] = rec.id
        return vals