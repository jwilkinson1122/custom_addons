from odoo import models, api, fields


class PrescriptionProduct(models.TransientModel):
    _name = 'prescription.product'
    # name = fields.Text(string='Description', required=True)

    prescription_id = fields.Many2one('podiatry.prescription', string='Prescription(Rx)')
    practice_id = fields.Char(related='prescription_id.practice_id.name')
    practitioner_id = fields.Char(related='prescription_id.practitioner_id.name')
    patient_id = fields.Char(related='prescription_id.patient_id.name')

    shell_foundation = fields.Many2one('product.product', string='Shell / Foundation',
                                       domain="[('categ_id', '=', 'Shell / Foundation')]")
    arch_height = fields.Many2one('product.product', string='Arch Height',
                                  domain="[('categ_id', '=', 'Arch Height')]")
    x_guard = fields.Many2one('product.product', string='X-Guard',
                              domain="[('categ_id', '=', 'X-Guard')]")
    top_cover = fields.Many2one('product.product', string='Top Cover',
                                domain="[('categ_id', '=', 'Top Cover')]")
    cushion = fields.Many2one('product.product', string='Cushion',
                              domain="[('categ_id', '=', 'Cushion')]")
    extension = fields.Many2one('product.product', string='Extension',
                                domain="[('categ_id', '=', 'Extension')]")

  

    def show_btn2(self):
        prescription_line = self.env['podiatry.prescription.line'].with_context(
            tracking_disable=True)
        prescription_line.create({
            'name': 'Product',
            'display_type': 'line_section',
            'prescription_id': self.env.context.get('active_id'),
        })
        prescription_line = self.env['podiatry.prescription.line'].create({
            'name': self.shell_foundation.name,
            'product_id': self.shell_foundation.id,
            'product_uom_qty': 1,
            'product_uom': self.shell_foundation.uom_id.id,
            'price_unit': self.shell_foundation.list_price,
            'prescription_id': self.env.context.get('active_id'),
        })
        prescription_line._onchange_product_id()

        prescription_line2 = self.env['podiatry.prescription.line'].create({
            'name': self.top_cover.name,
            'product_id': self.top_cover.id,
            'product_uom_qty': 2,
            'product_uom': self.top_cover.uom_id.id,
            'price_unit': self.top_cover.list_price,
            'prescription_id': self.env.context.get('active_id'),
        })
        prescription_line2._onchange_product_id()

        prescription_line3 = self.env['podiatry.prescription.line'].create({
            'name': self.arch_height.name,
            'product_id': self.arch_height.id,
            'product_uom_qty': 2,
            'product_uom': self.arch_height.uom_id.id,
            'price_unit': self.arch_height.list_price,
            'prescription_id': self.env.context.get('active_id'),
        })
        prescription_line3._onchange_product_id()

        prescription_line4 = self.env['podiatry.prescription.line'].create({
            'name': self.x_guard.name,
            'product_id': self.x_guard.id,
            'product_uom_qty': 2,
            'product_uom': self.x_guard.uom_id.id,
            'price_unit': self.x_guard.list_price,
            'prescription_id': self.env.context.get('active_id'),
        })
        prescription_line4._onchange_product_id()

        prescription_line5 = self.env['podiatry.prescription.line'].create({
            'name': self.cushion.name,
            'product_id': self.cushion.id,
            'product_uom_qty': 2,
            'product_uom': self.cushion.uom_id.id,
            'price_unit': self.cushion.list_price,
            'prescription_id': self.env.context.get('active_id'),
        })
        prescription_line5._onchange_product_id()

        prescription_line6 = self.env['podiatry.prescription.line'].create({
            'name': self.extension.name,
            'product_id': self.extension.id,
            'product_uom_qty': 2,
            'product_uom': self.extension.uom_id.id,
            'price_unit': self.extension.list_price,
            'prescription_id': self.env.context.get('active_id'),
        })
        prescription_line6._onchange_product_id()
 