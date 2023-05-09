import logging
from io import StringIO

from mako.runtime import Context
from mako.template import Template

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

logger = logging.getLogger(__name__)

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


class ProductProduct(models.Model):
    _inherit = "product.product"
    _rec_name = "config_name"

    def _get_conversions_dict(self):
        conversions = {"float": float, "integer": int}
        return conversions

    @api.constrains("product_template_attribute_value_ids")
    def _check_duplicate_product(self):
        """Check for prducts with same attribute values/custom values"""
        for product in self:
            if not product.config_ok:
                continue

            # At the moment, I don't have enough confidence with my
            # understanding of binary attributes, so will leave these
            # as not matching...
            # In theory, they should just work, if they are set to "non search"
            # in custom field def!
            # TODO: Check the logic with binary attributes
            config_session_obj = product.env["product.config.session"]
            ptav_ids = product.product_template_attribute_value_ids.mapped(
                "product_attribute_value_id"
            )
            duplicates = config_session_obj.search_variant(
                product_tmpl_id=product.product_tmpl_id,
                value_ids=ptav_ids.ids,
            ).filtered(lambda p: p.id != product.id)

            if duplicates:
                raise ValidationError(
                    _(
                        "Configurable Products cannot have duplicates "
                        "(identical attribute values)"
                    )
                )

    def _get_config_name(self):
        """Name for configured products
        :param: return : String"""
        self.ensure_one()
        return self.name

    def _get_mako_context(self, buf):
        """Return context needed for computing product name based
        on mako-tamplate define on it's product template"""
        self.ensure_one()
        ptav_ids = self.product_template_attribute_value_ids.mapped(
            "product_attribute_value_id"
        )
        return Context(
            buf,
            product=self,
            attribute_values=ptav_ids,
            steps=self.product_tmpl_id.config_step_line_ids,
            template=self.product_tmpl_id,
        )

    def _get_mako_tmpl_name(self):
        """Compute and return product name based on mako-tamplate
        define on it's product template"""
        self.ensure_one()
        if self.mako_tmpl_name:
            try:
                mytemplate = Template(self.mako_tmpl_name or "")
                buf = StringIO()
                ctx = self._get_mako_context(buf)
                mytemplate.render_context(ctx)
                return buf.getvalue()
            except Exception:
                logger.error(
                    _("Error while calculating mako product name: %s")
                    % self.display_name
                )
        return self.display_name

    @api.depends("product_template_attribute_value_ids.weight_extra")
    def _compute_product_weight_extra(self):
        for product in self:
            product.weight_extra = sum(
                product.mapped(
                    "product_template_attribute_value_ids.weight_extra")
            )

    def _compute_product_weight(self):
        for product in self:
            if product.config_ok:
                tmpl_weight = product.product_tmpl_id.weight
                product.weight = tmpl_weight + product.weight_extra
            else:
                product.weight = product.weight_dummy

    def _search_product_weight(self, operator, value):
        return [("weight_dummy", operator, value)]

    def _inverse_product_weight(self):
        """Store weight in dummy field"""
        self.weight_dummy = self.weight

    config_name = fields.Char(
        string="Configuration Name", compute="_compute_config_name"
    )
    weight_extra = fields.Float(compute="_compute_product_weight_extra")
    weight_dummy = fields.Float(string="Manual Weight", digits="Stock Weight")
    weight = fields.Float(
        compute="_compute_product_weight",
        inverse="_inverse_product_weight",
        search="_search_product_weight",
        store=False,
    )

    # product preset
    config_preset_ok = fields.Boolean(string="Is Preset")
    
    def get_product_multiline_description_prescription(self):
        name = self.display_name
        if self.description_prescription:
            name += '\n' + self.description_prescription

        return name

    # Replace action.
    def get_product_attribute_values_action(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "podiatry.product_attribute_value_action"
        )
        value_ids = self.product_template_attribute_value_ids.ids
        action["domain"] = [("id", "in", value_ids)]
        context = safe_eval(action["context"], {
                            "active_id": self.product_tmpl_id.id})
        context.update({"active_id": self.product_tmpl_id.id})
        action["context"] = context
        return action

    def _compute_config_name(self):
        """Compute the name of the configurable products and use template
        name for others"""
        for product in self:
            if product.config_ok:
                product.config_name = product._get_config_name()
            else:
                product.config_name = product.name

    def reconfigure_product(self):
        """launches a product configurator wizard with a linked
        template and variant in order to re-configure an existing product.
        It is essentially a shortcut to pre-fill configuration
        data of a variant"""
        self.ensure_one()

        extra_vals = {"product_id": self.id}
        return self.product_tmpl_id.create_config_wizard(extra_vals=extra_vals)

    @api.model
    def check_config_user_access(self, mode):
        """Check user have access to perform action(create/write/delete)
        on configurable products"""
        if not self.env["product.template"]._check_config_group_rights():
            return True
        config_manager = self.env.user.has_group(
            "podiatry.group_product_configurator_manager"
        )
        config_user = self.env.user.has_group(
            "podiatry.group_product_configurator"
        )
        user_root = self.env.ref("base.user_root")
        user_admin = self.env.ref("base.user_admin")
        if (
            config_manager
            or (config_user and mode not in ["delete"])
            or self.env.user.id in [user_root.id, user_admin.id]
        ):
            return True
        raise ValidationError(
            _(
                "Sorry, you are not allowed to create/change this kind of "
                "document. For more information please contact your manager."
            )
        )

    def unlink(self):
        """- Signal unlink from product variant through context so
        removal can be stopped for configurable templates
        - check access rights of user(configurable products)"""
        config_product = any(p.config_ok for p in self)
        if config_product:
            self.env["product.product"].check_config_user_access(mode="delete")
        ctx = dict(self.env.context, unlink_from_variant=True)
        self.env.context = ctx
        return super(ProductProduct, self).unlink()

    @api.model
    def create(self, vals):
        """Patch for check access rights of user(configurable products)"""
        config_ok = vals.get("config_ok", False)
        if config_ok:
            self.check_config_user_access(mode="create")
        return super(ProductProduct, self).create(vals)

    def write(self, vals):
        """Patch for check access rights of user(configurable products)"""
        change_config_ok = "config_ok" in vals
        configurable_products = self.filtered(
            lambda product: product.config_ok)
        if change_config_ok or configurable_products:
            self[:1].check_config_user_access(mode="write")

        return super(ProductProduct, self).write(vals)

    def _compute_product_price_extra(self):
        standard_products = self.filtered(
            lambda product: not product.config_ok)
        config_products = self - standard_products
        if standard_products:
            return super(
                ProductProduct, standard_products
            )._compute_product_price_extra()
        for product in config_products:
            attribute_value_obj = self.env["product.attribute.value"]
            value_ids = (
                product.product_template_attribute_value_ids.product_attribute_value_id
            )
            extra_prices = attribute_value_obj.get_attribute_value_extra_prices(
                product_tmpl_id=product.product_tmpl_id.id, pt_attr_value_ids=value_ids
            )
            product.price_extra = sum(extra_prices.values())

class ProductAttributeCustomValue(models.Model):
    _inherit = "product.attribute.custom.value"

    prescription_line_id = fields.Many2one('podiatry.prescription.line', string="Prescription Line", required=True, ondelete='cascade')

    _sql_constraints = [
        ('sol_custom_value_unique', 'unique(custom_product_template_attribute_value_id, prescription_line_id)', "Only one Custom Value is allowed per Attribute Value per Prescription Line.")
    ]
