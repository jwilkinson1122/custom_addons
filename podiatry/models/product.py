import logging
from io import StringIO

from mako.runtime import Context
from mako.template import Template

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class InheritedProduct(models.Model):
    _inherit = "product.product"

    is_helpdesk = fields.Boolean("Helpdesk Ticket?")
    helpdesk_team = fields.Many2one('helpdesk.team', string='Helpdesk Team')
    helpdesk_assigned_to = fields.Many2one('res.users', string='Assigned to')
    
    product_secondary_uom_id = fields.Many2one('uom.uom', 'Secondary Unit of Measure', 
        related="product_tmpl_id.secondary_uom", domain="[('category_id', '=', product_sec_product_uom_category_id)]",
        help="Default unit of measure used for all stock operations.", readonly=False)
    product_sec_product_uom_qty = fields.Float(string='S-Qty on Hand', digits='Product Unit of Measure',
        compute="_compute_product_sec_product_uom_qty", store=True)    
    product_sec_product_uom_category_id = fields.Many2one(related='product_tmpl_id.secondary_uom.category_id', string="Sec Product Category")
    
    @api.depends('qty_available')
    def _compute_product_sec_product_uom_qty(self):
        for record in self:
            if record.uom_id == record.product_secondary_uom_id:
                record.product_sec_product_uom_qty = record.qty_available
            elif record.product_secondary_uom_id.uom_type == 'reference' and record.uom_id.uom_type == 'bigger':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.qty_available

            elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'reference':
                record.product_sec_product_uom_qty = (record.uom_id.ratio / record.product_secondary_uom_id.ratio) * record.qty_available

            elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'reference':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.qty_available

            elif record.product_secondary_uom_id.uom_type == 'reference' and record.uom_id.uom_type == 'smaller':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio / record.uom_id.ratio) * record.qty_available 

            elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'bigger':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.qty_available 
                
            elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'smaller':
                record.product_sec_product_uom_qty = (1 / (record.product_secondary_uom_id.ratio * record.uom_id.ratio))* record.qty_available 

            elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'smaller':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio / record.uom_id.ratio) * record.qty_available
            
            elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'bigger':
                record.product_sec_product_uom_qty = (record.uom_id.ratio / record.product_secondary_uom_id.ratio) * record.qty_available

    # @api.onchange('product_sec_product_uom_qty')
    # def _inverse_product_sec_product_uom_qty(self):
    #     for record in self:
    #         if record.uom_id == record.product_secondary_uom_id:
    #             record.qty_available = record.product_sec_product_uom_qty            
    #         elif record.product_secondary_uom_id.uom_type == 'reference' and record.uom_id.uom_type == 'bigger':
    #             record.qty_available = (record.product_secondary_uom_id.ratio / record.uom_id.ratio) * record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'reference':
    #             record.qty_available = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'reference':
    #              record.qty_available = (record.uom_id.ratio / record.product_secondary_uom_id.ratio) * record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'reference' and record.uom_id.uom_type == 'smaller':
    #             record.qty_available = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'bigger':
    #             record.qty_available = (1 / (record.product_secondary_uom_id.ratio * record.uom_id.ratio))* record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'smaller':
    #             record.qty_available = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.product_sec_product_uom_qty


class ProductWithWeightInKg(models.Model):
    """Rename the field weight to `Weight in kg`."""

    _inherit = 'product.product'

    weight = fields.Float(string='Weight in kg')


class ProductWithWeightWithTrackVisibility(models.Model):
    """Add track_visibility to the field weight."""

    _inherit = 'product.product'

    weight = fields.Float(tracking=True)


class ProductWithWeightInUoM(models.Model):
    """Add the fields weight_in_uom and specific_weight_uom_id to products.

    The weight can not be negative.
    """

    _inherit = 'product.product'

    weight_in_uom = fields.Float(
        'Weight', digits='Stock Weight',
        tracking=True)

    specific_weight_uom_id = fields.Many2one(
        'uom.uom', 'Weight UoM', ondelete='restrict',
        tracking=True)

    @api.constrains('weight_in_uom')
    def _check_weight_is_not_negative(self):
        """Check that dimensions are strictly positive."""
        for product in self:
            if product.weight_in_uom < 0:
                raise ValidationError(_(
                    'The weight of a product ({product}) can not be negative.'
                ).format(product=product.display_name))

    @api.model
    def create(self, vals):
        """After creating a product, synchronize its weight in Kg with its weight in uom.

        A product can be created with either the weight in Kg or the weight in the
        product's unit of measure.
        """
        vals_copy = vals.copy()
        res = super().create(vals)

        if vals_copy.get('weight_in_uom'):
            res.update_weight_from_weight_in_uom()

        elif vals_copy.get('weight'):
            res.update_weight_in_uom_from_weight()

        return res

    def write(self, vals):
        """Synchronize the weight in Kg and the weight in the uom of the product.

        Changing the value of one of the 2 fields should update the value for the other.
        """
        vals_copy = vals.copy()
        super().write(vals)

        updating_weight_in_uom = 'weight_in_uom' in vals_copy or 'specific_weight_uom_id' in vals_copy
        updating_weight_in_uom_from_weight = self._context.get(
            'updating_weight_in_uom_from_weight')

        updating_weight = 'weight' in vals_copy
        updating_weight_from_weight_in_uom = self._context.get(
            'updating_weight_from_weight_in_uom')

        if updating_weight_in_uom and not updating_weight_in_uom_from_weight:
            for record in self:
                record.update_weight_from_weight_in_uom()

        elif updating_weight and not updating_weight_from_weight_in_uom:
            for record in self:
                record.update_weight_in_uom_from_weight()

        return True

    def update_weight_from_weight_in_uom(self):
        """Update the weight in kg from the weight in uom."""
        uom_kg = self.env.ref('uom.product_uom_kgm')
        weight = self.specific_weight_uom_id._compute_quantity(
            self.weight_in_uom, uom_kg)
        self.with_context(updating_weight_from_weight_in_uom=True).write(
            {'weight': weight})

    def update_weight_in_uom_from_weight(self):
        """Update the weight in uom from the weight in kg."""
        uom_kg = self.env.ref('uom.product_uom_kgm')
        uom = self.specific_weight_uom_id or uom_kg
        weight_in_uom = uom_kg._compute_quantity(self.weight, uom)
        self.with_context(updating_weight_in_uom_from_weight=True).write({
            'weight_in_uom': weight_in_uom,
            'specific_weight_uom_id': uom.id,
        })


class ProductWithDimensions(models.Model):
    """Add dimension fields to products."""

    _inherit = 'product.product'

    height = fields.Float(
        'Height',
        tracking=True,
        digits='Product Dimension',
    )

    length = fields.Float(
        'Length',
        tracking=True,
        digits='Product Dimension',
    )

    width = fields.Float(
        'Width',
        tracking=True,
        digits='Product Dimension',
    )

    dimension_uom_id = fields.Many2one(
        'uom.uom', 'Dimension UoM', ondelete='restrict',
        tracking=True)

    @api.constrains('height')
    def _check_height_is_not_negative(self):
        """Check that dimensions are strictly positive."""
        for product in self:
            if product.height < 0:
                raise ValidationError(_(
                    'The height of a product ({product}) can not be negative.'
                ).format(product=product.display_name))

    @api.constrains('length')
    def _check_length_is_not_negative(self):
        """Check that dimensions are strictly positive."""
        for product in self:
            if product.length < 0:
                raise ValidationError(_(
                    'The length of a product ({product}) can not be negative.'
                ).format(product=product.display_name))

    @api.constrains('width')
    def _check_width_is_not_negative(self):
        """Check that dimensions are strictly positive."""
        for product in self:
            if product.width < 0:
                raise ValidationError(_(
                    'The width of a product ({product}) can not be negative.'
                ).format(product=product.display_name))


class ProductWithVolumeDecimalPrecision(models.Model):
    """Add a decimal precision to the volume of a product."""

    _inherit = 'product.product'

    volume = fields.Float(digits='Product Volume')


class ProductWithVolumeComputedFromDimensions(models.Model):
    """Compute the field volume from dimension fields."""

    _inherit = 'product.product'

    volume = fields.Float(compute='_compute_volume', store=True)

    def _get_volume_without_rounding(self):
        """Get the volume of the product without rounding the result."""
        meter = self.env.ref('uom.product_uom_meter')

        def to_meter(from_uom, dimension):
            """Convert a dimension from a given uom to meter.

            :param from_uom: the unit of measure of the dimension to convert
            :param dimension: the dimension to convert
            :return: the dimension in meter
            """
            return from_uom._compute_quantity(dimension, meter, round=False)

        height_in_meter = to_meter(self.dimension_uom_id, self.height)
        length_in_meter = to_meter(self.dimension_uom_id, self.length)
        width_in_meter = to_meter(self.dimension_uom_id, self.width)

        return height_in_meter * length_in_meter * width_in_meter

    @api.depends('height', 'length', 'width', 'dimension_uom_id')
    def _compute_volume(self):
        """Compute the volume of the product."""
        for product in self:
            product.volume = product._get_volume_without_rounding()


class ProductWithDensity(models.Model):
    """Add the field density to products."""

    _inherit = 'product.product'

    density = fields.Float(
        'Density',
        compute='_compute_density',
        digits='Product Density',
        store=True,
    )

    @api.depends('weight', 'height', 'length', 'width', 'dimension_uom_id')
    def _compute_density(self):
        """Compute the density of the product.

        For computing the volume, we use the volume without rounding.
        A very small volume will result in a very high density.
        Therefore, the precision in units of measure has an important impact on
        the result.
        """
        for product in self:
            volume = product._get_volume_without_rounding()
            product.density = product.weight / volume if volume else None

