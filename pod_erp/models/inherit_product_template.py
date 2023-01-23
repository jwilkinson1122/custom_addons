from odoo import models, api, fields


class ProductFromTemp(models.Model):
    _inherit = 'product.template'

    shell_material = fields.Many2one('shell.material', string='Material')
    shell_shape = fields.Many2one('shell.shape', string='Shape')
    shell_type = fields.Many2one('shell.type', string='Shell / Founation Type')
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('other', 'Others')])
    # age = fields.Selection([('Male', 'Female', 'Others')])
    manufacturer = fields.Many2one('shell.manufacturer', string='Manufacturer')
    brand = fields.Many2one('shell.brand', string='Brand')
    rim = fields.Selection(
        [('3-Piece Compression', '3-Piece Compression'), ('3-Piece Screw', '3-Piece Screw'), ('Full Rim', 'Full Rim'),
         ('Half Rim', 'Half Rim'), ('Inverted Half Rim', 'Inverted Half Rim'),
         ('Semi-Rimless', 'Semi-Rimless'), ('Shield', 'Shield'), ('Other', 'Other'), ('None', 'None')])
    collection = fields.Many2one('shell.collection', string='Collection')

    topcover_type = fields.Many2one('topcover.type', string='Topcover Type')
    topcover_style = fields.Many2one('topcover.style', string='Topcover Style')
    topcover_material = fields.Many2one('topcover.material', string='Material')

    @api.model
    def default_get(self, vals):
        if self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Shells':
            self.categ_id = self.env.ref('pod_erp.product_category_shells').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Topcover':
            self.categ_id = self.env.ref(
                'pod_erp.product_category_Topcover').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Topcover Treatment':
            self.categ_id = self.env.ref(
                'pod_erp.product_category_TopcoverTreatment').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Service':
            self.categ_id = self.env.ref('pod_erp.product_category_service').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Miscellaneous':
            self.categ_id = self.env.ref(
                'pod_erp.product_category_miscellaneous').id
        return super(ProductFromTemp, self).default_get(vals)
