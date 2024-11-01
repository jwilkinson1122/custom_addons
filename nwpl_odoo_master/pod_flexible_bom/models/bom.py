from odoo import fields, models, api


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    bom_template_id = fields.Many2one("mrp.bom", string="BOM Template")

    @api.onchange('bom_template_id')
    def _onchange_bom_template_id(self):
        if self.bom_template_id:
            # Clear existing lines
            self.bom_line_ids = [(5, 0, 0)]

            # Add lines from the template
            new_lines = []
            for line in self.bom_template_id.bom_line_ids:
                new_line_vals = {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'product_uom_id': line.product_uom_id.id,
                }
                new_lines.append((0, 0, new_line_vals))
            self.bom_line_ids = new_lines
