from odoo import models, api, fields


class ProductFromTemp(models.Model):
    _inherit = 'product.template'
    
    is_helpdesk = fields.Boolean("Helpdesk Ticket?")
    helpdesk_team = fields.Many2one('helpdesk.team', string='Helpdesk Team')
    helpdesk_assigned_to = fields.Many2one('res.users', string='Assigned to')
    
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id
                                  .currency_id.id,
                                  required=True)
    device_ok = fields.Boolean('Device')
    product_prices = fields.Monetary('Price', help="Price of the products")

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
    
    @api.onchange('device_ok')
    def onchange_product_type(self):
        self.type = 'consu'
        self.list_price = self.product_prices

    @api.model
    def default_get(self, vals):
        if self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Frames':
            self.categ_id = self.env.ref('pod_erp.product_category_frames').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Contact Lens':
            self.categ_id = self.env.ref('pod_erp.product_category_contactLens').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Lens':
            self.categ_id = self.env.ref('pod_erp.product_category_Lens').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Lens Treatment':
            self.categ_id = self.env.ref('pod_erp.product_category_LensTreatment').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Service':
            self.categ_id = self.env.ref('pod_erp.product_category_service').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Miscellaneous':
            self.categ_id = self.env.ref('pod_erp.product_category_miscellaneous').id
        return super(ProductFromTemp, self).default_get(vals)

    @api.model
    def create(self, vals):
        templates = super (ProductFromTemp,self).create(vals)
        if templates.product_variant_count <= 1:
            if templates.product_variant_id:
                templates.product_variant_id.is_helpdesk = templates.is_helpdesk
                templates.product_variant_id.helpdesk_team = templates.helpdesk_team.id
                templates.product_variant_id.helpdesk_assigned_to = templates.helpdesk_assigned_to.id
        return templates

    def write(self, vals):
        res = super(ProductFromTemp, self).write(vals)
        if not self.product_variant_count > 1:
            if self.product_variant_id:
                self.product_variant_id.is_helpdesk = self.is_helpdesk
                self.product_variant_id.helpdesk_team = self.helpdesk_team
                self.product_variant_id.helpdesk_assigned_to = self.helpdesk_assigned_to
        else:
            if self.product_variant_id:
                self.product_variant_id.is_helpdesk = False
                self.product_variant_id.helpdesk_team.unlink()
                self.product_variant_id.helpdesk_assigned_to.unlink()

        return res