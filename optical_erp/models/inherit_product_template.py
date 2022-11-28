from odoo import models, api, fields


class ProductFromTemp(models.Model):
    _inherit = 'product.template'

    frame_material = fields.Many2one('frame.material', string='Material')
    frame_shape = fields.Many2one('frame.shape', string='Shape')
    frame_type = fields.Many2one('frame.type', string='Frame Type')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Others')])
    # age = fields.Selection([('Male', 'Female', 'Others')])
    manufacturer = fields.Many2one('frame.manufacturer', string='Manufacturer')
    brand = fields.Many2one('frame.brand', string='Brand')
    rim = fields.Selection(
        [('3-Piece Compression', '3-Piece Compression'), ('3-Piece Screw', '3-Piece Screw'), ('Full Rim', 'Full Rim'),
         ('Half Rim', 'Half Rim'), ('Inverted Half Rim', 'Inverted Half Rim'),
         ('Semi-Rimless', 'Semi-Rimless'), ('Shield', 'Shield'), ('Other', 'Other'), ('None', 'None')])
    collection = fields.Many2one('frame.collection', string='Collection')

    lens_type = fields.Many2one('lens.type', string='Lens Type')
    lens_style = fields.Many2one('lens.style', string='Lens Style')
    lens_material = fields.Many2one('lens.material', string='Material')
    contact_lens_manufacturer = fields.Many2one('contact.lens.manufacturer', string='Manufacturer')

    @api.model
    def default_get(self, vals):
        if self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Frames':
            self.categ_id = self.env.ref('optical_erp.product_category_frames').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Contact Lens':
            self.categ_id = self.env.ref('optical_erp.product_category_contactLens').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Lens':
            self.categ_id = self.env.ref('optical_erp.product_category_Lens').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Lens Treatment':
            self.categ_id = self.env.ref('optical_erp.product_category_LensTreatment').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Service':
            self.categ_id = self.env.ref('optical_erp.product_category_service').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Miscellaneous':
            self.categ_id = self.env.ref('optical_erp.product_category_miscellaneous').id
        return super(ProductFromTemp, self).default_get(vals)
