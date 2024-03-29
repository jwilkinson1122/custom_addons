# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    is_prescription = fields.Boolean(default=False)
    is_device = fields.Boolean(string='Is Product')
    is_option = fields.Boolean(string='Is Option')
    is_custom_device = fields.Boolean(default=False, help="True if product is a brace")   
    is_otc_device = fields.Boolean(default=False, help="True if product does not require a prescription") 
    is_brace_device = fields.Boolean(default=False, help="True if product is a brace")  
    is_helpdesk = fields.Boolean("Helpdesk Ticket?")
    helpdesk_team = fields.Many2one('helpdesk.team', string='Helpdesk Team')
    helpdesk_assigned_to = fields.Many2one('res.users', string='Assigned to')
    
    @tools.ormcache()
    def _get_default_secondary_uom(self):
        return self.env.ref('uom.product_uom_dozen')
    
    secondary_uom_active = fields.Boolean(string='Secondary Unit ?', default=True)
    secondary_uom = fields.Many2one('uom.uom', 'Secondary Unit of Measure', required=True, help="Default unit of measure used for all stock operations.", default=_get_default_secondary_uom)
    
    uom_name = fields.Char(string='Sec UoM Name', related='secondary_uom.name', readonly=True)
    on_hand_qty = fields.Float(
        'Quantity On Hand', compute='_compute_on_hand_qty', digits='Product Unit of Measure', compute_sudo=False, help="Current quantity of products.\n"
             "In a context with a single Stock Location, this includes "
             "goods stored at this Location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods stored in the Stock Location of this Warehouse, or any "
             "of its children.\n"
             "stored in the Stock Location of the Warehouse of this Shop, "
             "or any of its children.\n"
             "Otherwise, this includes goods stored in any Stock Location "
             "with 'internal' type.")

    # def _compute_on_hand_qty(self):
    #     self.on_hand_qty = self.qty_available
    @api.depends('qty_available')
    def _compute_on_hand_qty(self):
        for record in self:
            if record.uom_id == record.secondary_uom:
                record.on_hand_qty = record.qty_available
            elif record.secondary_uom.uom_type == 'reference' and record.uom_id.uom_type == 'bigger':
                record.on_hand_qty = (record.secondary_uom.ratio * record.uom_id.ratio) * record.qty_available

            elif record.secondary_uom.uom_type == 'bigger' and record.uom_id.uom_type == 'reference':
                record.on_hand_qty = (record.uom_id.ratio / record.secondary_uom.ratio) * record.qty_available

            elif record.secondary_uom.uom_type == 'smaller' and record.uom_id.uom_type == 'reference':
                record.on_hand_qty = (record.secondary_uom.ratio * record.uom_id.ratio) * record.qty_available

            elif record.secondary_uom.uom_type == 'reference' and record.uom_id.uom_type == 'smaller':
                record.on_hand_qty = (record.secondary_uom.ratio / record.uom_id.ratio) * record.qty_available 

            elif record.secondary_uom.uom_type == 'smaller' and record.uom_id.uom_type == 'bigger':
                record.on_hand_qty = (record.secondary_uom.ratio * record.uom_id.ratio) * record.qty_available 
                
            elif record.secondary_uom.uom_type == 'bigger' and record.uom_id.uom_type == 'smaller':
                record.on_hand_qty = (1 / (record.secondary_uom.ratio * record.uom_id.ratio))* record.qty_available

            elif record.secondary_uom.uom_type == 'smaller' and record.uom_id.uom_type == 'smaller':
                record.on_hand_qty = (record.secondary_uom.ratio / record.uom_id.ratio) * record.qty_available
            
            elif record.secondary_uom.uom_type == 'bigger' and record.uom_id.uom_type == 'bigger':
                record.on_hand_qty = (record.uom_id.ratio / record.secondary_uom.ratio) * record.qty_available

    @api.model
    def create(self, vals):
        templates = super (ProductTemplateInherit,self).create(vals)
        if templates.product_variant_count<= 1:
            if templates.product_variant_id:
                templates.product_variant_id.is_helpdesk = templates.is_helpdesk
                templates.product_variant_id.helpdesk_team = templates.helpdesk_team.id
                templates.product_variant_id.helpdesk_assigned_to = templates.helpdesk_assigned_to.id
        return templates

    def write(self, vals):
        res = super(ProductTemplateInherit, self).write(vals)
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
 
    shell_type = fields.Many2one(
        'shell.type', string='Shell / Foundation Type')
    shell_collection = fields.Many2one(
        'shell.collection', string='Shell Collection')
    topcover_type = fields.Many2one('topcover.type', string='Top Cover Type')
    topcover_length = fields.Many2one(
        'topcover.length', string='Top Cover Length')
    topcover_material = fields.Many2one(
        'topcover.material', string='Top Cover Material')
    topcover_thickness = fields.Many2one(
        'topcover.thickness', string='Top Cover Thickness')
    topcover_color = fields.Many2one(
        'topcover.color', string='Top Cover Color')
    arch_height_type = fields.Many2one(
        'arch.height.type', string='Arch Height')
    xguard_length = fields.Many2one('x_guard.length', string='X-Guard Length')
    cushion_type = fields.Many2one('cushion.type', string='Cushion Type')
    cushion_material = fields.Many2one(
        'cushion.material', string='Cushion Material')
    cushion_length = fields.Many2one('cushion.length', string='Cushion Length')
    cushion_thickness = fields.Many2one(
        'cushion.thickness', string='Cushion Thickness')
    extension_type = fields.Many2one('extension.type', string='Cushion Type')
    extension_material = fields.Many2one(
        'extension.material', string='Cushion Material')
    extension_length = fields.Many2one(
        'extension.length', string='Cushion Length')
    extension_thickness = fields.Many2one(
        'extension.thickness', string='Cushion Thickness')

    rim = fields.Selection(
        [('3-Piece Compression', '3-Piece Compression'), ('3-Piece Screw', '3-Piece Screw'), ('Full Rim', 'Full Rim'),
         ('Half Rim', 'Half Rim'), ('Inverted Half Rim', 'Inverted Half Rim'),
         ('Semi-Rimless', 'Semi-Rimless'), ('Shield', 'Shield'), ('Other', 'Other'), ('None', 'None')])

    @api.model
    def default_get(self, vals):
        if self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Shell / Foundation':
            self.categ_id = self.env.ref('pod_order_management.product_category_shells').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Top Covers':
            self.categ_id = self.env.ref(
                'pod_order_management.product_category_top_covers').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Arch Height':
            self.categ_id = self.env.ref(
                'pod_order_management.product_category_arch_height').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'X-Guard':
            self.categ_id = self.env.ref(
                'pod_order_management.product_category_x_guard').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Cushion':
            self.categ_id = self.env.ref(
                'pod_order_management.product_category_cushion').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Extension':
            self.categ_id = self.env.ref(
                'pod_order_management.product_category_extension').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Accommodation':
            self.categ_id = self.env.ref(
                'pod_order_management.product_category_accommodation').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Service':
            self.categ_id = self.env.ref(
                'pod_order_management.product_category_service').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Miscellaneous':
            self.categ_id = self.env.ref(
                'pod_order_management.product_category_miscellaneous').id
        return super(ProductTemplateInherit, self).default_get(vals)

   
class ProductTemplateWithWeightInKg(models.Model):
    """Rename the field weight to `Weight in Kg`."""

    _inherit = 'product.template'

    weight = fields.Float(string='Weight in Kg')


class ProductTemplateWithWeightInUoM(models.Model):
    """Add the fields weight_in_uom and specific_weight_uom_id to products."""

    _inherit = 'product.template'

    weight_in_uom = fields.Float( related='product_variant_ids.weight_in_uom', readonly=False, store=True,
    )

    specific_weight_uom_id = fields.Many2one( related='product_variant_ids.specific_weight_uom_id', readonly=False, store=True,
    )


class ProductTemplateWithDimensions(models.Model):
    """Add dimension fields to products."""

    _inherit = 'product.template'

    height = fields.Float( related='product_variant_ids.height', readonly=False, store=True,
    )

    length = fields.Float( related='product_variant_ids.length', readonly=False, store=True,
    )

    width = fields.Float( related='product_variant_ids.width', readonly=False, store=True,
    )

    dimension_uom_id = fields.Many2one( related='product_variant_ids.dimension_uom_id', readonly=False, store=True,
    )


class ProductTemplatePropagateFieldsOnCreate(models.Model):
    """Properly save dimensions on the variant when creating a product template.

    At the creation of the product template, the related field values are not passed
    over to the related variant, because the variant is created after the template.

    Therefore, those fields need to be propagated to the variant after the create process.
    """

    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        template = super().create(vals)

        fields_to_propagate = (
            'weight_in_uom', 'specific_weight_uom_id',
            'height', 'length', 'width', 'dimension_uom_id',
        )

        vals_to_propagate = {k: v for k,
                             v in vals.items() if k in fields_to_propagate}

        for variant in template.product_variant_ids:
            # Only write values that are different from the variant's default value.
            changed_values_to_propagate = {
                k: v for k, v in vals_to_propagate.items()
                if (v or variant[k]) and v != variant[k]
            }
            variant.write(changed_values_to_propagate)

        return template


class ProductTemplateWithVolumeRelated(models.Model):
    """Make the volume related to the volume on the variant.

    In the odoo source code, the field volume is computed instead of related.

    The problem is that when the volume is recomputed on product.product
    (because a dimension changes), the new volume is not propagated to product.template.

    In other words, the following use of api.depends:

        @api.depends('product_variant_ids', 'product_variant_ids.volume')

    does not work if volume is computed (even if it is stored).
    """

    _inherit = 'product.template'

    volume = fields.Float( related='product_variant_ids.volume', store=True,
    )


class ProductTemplateWithDensity(models.Model):
    """Add the field density to products."""

    _inherit = 'product.template'

    density = fields.Float(
        'Density', related='product_variant_ids.density', store=True,
    )
