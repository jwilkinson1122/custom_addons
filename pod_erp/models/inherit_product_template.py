from odoo import models, api, fields


class ProductFromTemp(models.Model):
    _inherit = 'product.template'

    topcover_material = fields.Many2one('topcover.material', string='Material')
    topcover_shape = fields.Many2one('topcover.length', string='Shape')
    topcover_type = fields.Many2one('topcover.type', string='Top Cover Type')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Others')])
    # age = fields.Selection([('Male', 'Female', 'Others')])
    manufacturer = fields.Many2one('topcover.manufacturer', string='Manufacturer')
    brand = fields.Many2one('topcover.brand', string='Brand')
    rim = fields.Selection(
        [('3-Piece Compression', '3-Piece Compression'), ('3-Piece Screw', '3-Piece Screw'), ('Full Rim', 'Full Rim'),
         ('Half Rim', 'Half Rim'), ('Inverted Half Rim', 'Inverted Half Rim'),
         ('Semi-Rimless', 'Semi-Rimless'), ('Shield', 'Shield'), ('Other', 'Other'), ('None', 'None')])
    collection = fields.Many2one('topcover.collection', string='Collection')

    lens_type = fields.Many2one('lens.type', string='Lens Type')
    lens_style = fields.Many2one('lens.style', string='Lens Style')
    lens_material = fields.Many2one('lens.material', string='Material')
    
    @api.model
    def default_get(self, vals):
        if self._context.get('def_categ_id', False) and self._context.get('def_categ_id', False) == 'Top Covers':
            demo_categ = self.env.ref('pod_erp.product_category_topcovers', False)
            self.categ_id = demo_categ.id
        elif self._context.get('def_categ_id', False) and self._context.get('def_categ_id', False) == 'Lens':
            demo_categ = self.env.ref('pod_erp.product_category_Lens', False)
            self.categ_id = demo_categ.id
        elif self._context.get('def_categ_id', False) and self._context.get('def_categ_id', False) == 'Lens Treatment':
            demo_categ = self.env.ref('pod_erp.product_category_LensTreatment', False)
            self.categ_id = demo_categ.id
        elif self._context.get('def_categ_id', False) and self._context.get('def_categ_id', False) == 'Service':
            demo_categ = self.env.ref('pod_erp.product_category_service', False)
            self.categ_id = demo_categ.id
        elif self._context.get('def_categ_id', False) and self._context.get('def_categ_id', False) == 'Miscellaneous':
            demo_categ = self.env.ref('pod_erp.product_category_miscellaneous', False)
            self.categ_id = demo_categ.id
        return super(ProductFromTemp, self).default_get(vals)
