from odoo import fields, models, api, _


class ManufacturingOrderWizard(models.TransientModel):
    _name = 'mo.wizard'
    _description = 'Manufacturing Order Wizard'



    product_id = fields.Many2one('product.template', string="Final Product")
    component_ids = fields.Many2many('mrp.bom', string="Components")
    product_ids = fields.Many2many('product.template', string="Products")


    def create_bom(self):
        for rec in self:
            product_list = []
            for bom in rec.component_ids:
                product_list.append(bom.product_tmpl_id.id)
            for product in rec.product_ids:
                product_list.append(product.id)
            bom = self.env['mrp.bom'].search('product_tmpl_id','',rec.product_id.id)
            print(bom.name,"<<<<<<<<<<<<<<<<<<<<<<<<<<")
            self.env['mrp.bom'].write({
                'product_tmpl_id' : rec.product_id.id,
                'bom_line_ids': product_list
            })


class ProductProductInherit(models.Model):
    _inherit = 'product.template'

    bom_id = fields.Many2one('mrp.bom', string="BoM")