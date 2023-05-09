import itertools
import logging
from collections import defaultdict

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, RedirectWarning, UserError
from odoo.osv import expression

logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    description_prescription = fields.Text('Prescription Description', translate=True, help="A description of the Product. "
             "This description will be copied to every Prescription Order, Sale Order, Delivery Order and Customer Invoice/Credit Note")


    is_prescription = fields.Boolean(default=False)
    is_custom_device = fields.Boolean(default=False, help="True if product is a brace")  # Field: isBrace
    is_otc_device = fields.Boolean(default=False, help="True if product does not require a prescription")  # Field: isOverTheCounter
    is_brace_device = fields.Boolean(default=False, help="True if product is a brace")  # Field: isBrace
    foot_selection = fields.Selection([('left_only', 'Left Only'), ('right_only', 'Right Only'), ('bilateral', 'Bilateral')], default='bilateral')
    
    detailed_type = fields.Selection(selection_add=[('product', 'Product')], ondelete={'product': 'set consu'})

    @api.onchange('detailed_type')
    def _onchange_type_product(self):
        if self.detailed_type == 'product':
            self.invoice_policy = 'order'

    def _detailed_type_mapping(self):
        type_mapping = super()._detailed_type_mapping()
        type_mapping['product'] = 'consu'
        return type_mapping

    shell_type = fields.Many2one('shell.type', string='Shell / Foundation Type')
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
        if self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Athletic':
            self.categ_id = self.env.ref('podiatry.product_category_athletic').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Shell / Foundation':
                self.categ_id = self.env.ref(
                'podiatry.product_category_shells').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Top Covers':
            self.categ_id = self.env.ref(
                'podiatry.product_category_top_covers').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Arch Height':
            self.categ_id = self.env.ref(
                'podiatry.product_category_arch_height').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'X-Guard':
            self.categ_id = self.env.ref(
                'podiatry.product_category_x_guard').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Cushion':
            self.categ_id = self.env.ref(
                'podiatry.product_category_cushion').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Extension':
            self.categ_id = self.env.ref(
                'podiatry.product_category_extension').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Accommodation':
            self.categ_id = self.env.ref(
                'podiatry.product_category_accommodation').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Service':
            self.categ_id = self.env.ref(
                'podiatry.product_category_service').id
        elif self._context.get('def_categ_id') and self._context.get('def_categ_id') == 'Miscellaneous':
            self.categ_id = self.env.ref(
                'podiatry.product_category_miscellaneous').id
        return super(ProductTemplate, self).default_get(vals)

    uom_measure_type = fields.Selection(
        string="UoM Type of Measure",
        related="uom_id.measure_type",
        store=True,
        readonly=True,
    )

    product_length = fields.Float(string="Length", default=1)
    product_width = fields.Float(string="Width", default=1)
    product_height = fields.Float(string="Height", default=1)
    
    dimensions_uom_id = fields.Many2one(
        'uom.uom',
        'Dimension(UOM)',
        domain = lambda self:[('category_id','=',self.env.ref('uom.uom_categ_length').id)],
        help="Default Unit of Measure used for dimension."
    )

    weight_uom_id = fields.Many2one(
        'uom.uom',
        'Weight(UOM)',
        domain = lambda self:[('category_id','=',self.env.ref('uom.product_uom_categ_kgm').id)],
        help="Default Unit of Measure used for weight."
    )

    @api.onchange("product_length", "product_width", "product_height")
    def _onchange_dimension(self):
        if self.product_length and self.product_width and self.product_height:
            self.volume = self.product_length * self.product_width * self.product_height / 1000000
    

    @tools.ormcache()
    def _get_default_secondary_uom(self):
        return self.env.ref('uom.product_uom_unit')
    
    secondary_uom_active = fields.Boolean(string='Secondary Unit ?', default=True)
    secondary_uom = fields.Many2one('uom.uom', 'Secondary Unit of Measure', 
        required=True, help="Default unit of measure used for all stock operations.",
        default=_get_default_secondary_uom)
    
    uom_name = fields.Char(string='Sec UoM Name', related='secondary_uom.name', readonly=True)
    on_hand_qty = fields.Float(
        'Quantity On Hand', compute='_compute_on_hand_qty',
        digits='Product Unit of Measure', compute_sudo=False,
        help="Current quantity of products.\n"
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

    @api.depends("product_variant_ids.product_tmpl_id")
    def _compute_product_variant_count(self):
        """For configurable products return the number of variants configured or
        1 as many views and methods trigger only when a template has at least
        one variant attached. Since we create them from the template we should
        have access to them always"""
        res = super(ProductTemplate, self)._compute_product_variant_count()
        for product_tmpl in self:
            config_ok = product_tmpl.config_ok
            variant_count = product_tmpl.product_variant_count
            if config_ok and not variant_count:
                product_tmpl.product_variant_count = 1
        return res

    @api.depends("attribute_line_ids.value_ids")
    def _compute_template_attr_vals(self):
        """Compute all attribute values added in attribute line on
        product template"""
        for product_tmpl in self:
            if product_tmpl.config_ok:
                value_ids = product_tmpl.attribute_line_ids.mapped("value_ids")
                product_tmpl.attribute_line_val_ids = value_ids
            else:
                product_tmpl.attribute_line_val_ids = False

    @api.constrains("type", "is_prescription")
    def _check_product(self):
        if self.is_prescription:
            if self.type not in ["product", "consu"]:
                raise ValidationError(
                    _("Must be a stockable product")
                )

    @api.constrains("attribute_line_ids", "attribute_value_line_ids")
    def check_attr_value_ids(self):
        """Check attribute lines don't have some attribute value that
        is not present in attribute lines of that product template"""
        for product_tmpl in self:
            if not product_tmpl.env.context.get("check_constraint", True):
                continue
            attr_val_lines = product_tmpl.attribute_value_line_ids
            attr_val_ids = attr_val_lines.mapped("value_ids")
            if not attr_val_ids <= product_tmpl.attribute_line_val_ids:
                raise ValidationError(
                    _(
                        "All attribute values used in attribute value lines "
                        "must be defined in the attribute lines of the "
                        "template"
                    )
                )

    @api.constrains("attribute_value_line_ids")
    def _validate_unique_config(self):
        """Check for duplicate configurations for the same
        attribute value in image lines"""
        for template in self:
            attr_val_line_vals = template.attribute_value_line_ids.read(
                ["value_id", "value_ids"], load=False
            )
            attr_val_line_vals = [
                (line["value_id"], tuple(line["value_ids"]))
                for line in attr_val_line_vals
            ]
            if len(set(attr_val_line_vals)) != len(attr_val_line_vals):
                raise ValidationError(
                    _("You cannot have a duplicate configuration for the " "same value")
                )

    config_ok = fields.Boolean(string="Can be Configured")

    config_line_ids = fields.One2many(
        comodel_name="product.config.line",
        inverse_name="product_tmpl_id",
        string="Attribute Dependencies",
        copy=False,
    )

    config_image_ids = fields.One2many(
        comodel_name="product.config.image",
        inverse_name="product_tmpl_id",
        string="Configuration Images",
        copy=True,
    )

    attribute_value_line_ids = fields.One2many(
        comodel_name="product.attribute.value.line",
        inverse_name="product_tmpl_id",
        string="Attribute Value Lines",
        copy=True,
    )

    attribute_line_val_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        compute="_compute_template_attr_vals",
        store=False,
    )

    config_step_line_ids = fields.One2many(
        comodel_name="product.config.step.line",
        inverse_name="product_tmpl_id",
        string="Configuration Lines",
        copy=False,
    )

    mako_tmpl_name = fields.Text(
        string="Variant name",
        help="Generate Name based on Mako Template",
        copy=True,
    )

    # We are calculating weight of variants based on weight of
    # product-template so that no need of compute and inverse on this
    weight = fields.Float(
        compute="_compute_weight",
        inverse="_set_weight",  # pylint: disable=C8110
        search="_search_weight",
        store=False,
    )
    weight_dummy = fields.Float(
        string="Manual Weight",
        digits="Stock Weight",
        help="Manual setting of product template weight",
    )

    def _compute_weight(self):
        config_products = self.filtered(lambda template: template.config_ok)
        for product in config_products:
            product.weight = product.weight_dummy
        standard_products = self - config_products
        return super(ProductTemplate, standard_products)._compute_weight()

    def _set_weight(self):
        for product_tmpl in self:
            product_tmpl.weight_dummy = product_tmpl.weight
            if not product_tmpl.config_ok:
                return super(ProductTemplate, product_tmpl)._set_weight()

    def _search_weight(self, operator, value):
        return [("weight_dummy", operator, value)]

    # Replace action.
    def get_product_attribute_values_action(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "podiatry.product_attribute_value_action"
        )
        value_ids = self.attribute_line_ids.mapped(
            "product_template_value_ids").ids
        action["domain"] = [("id", "in", value_ids)]
        context = safe_eval(action["context"], {"active_id": self.id})
        context.update({"active_id": self.id})
        action["context"] = context
        return action

    def _check_default_values(self):
        default_val_ids = (
            self.attribute_line_ids.filtered(lambda l: l.default_val)
            .mapped("default_val")
            .ids
        )

        cfg_session_obj = self.env["product.config.session"]
        try:
            cfg_session_obj.validate_configuration(
                value_ids=default_val_ids, product_tmpl_id=self.id, final=False
            )
        except ValidationError as ex:
            raise ValidationError(ex) from ex
        except Exception as err:
            raise ValidationError(
                _("Default values provided generate an invalid configuration")
            ) from err

    @api.constrains("config_line_ids", "attribute_line_ids")
    def _check_default_value_domains(self):
        for template in self:
            try:
                template._check_default_values()
            except ValidationError as e:
                raise ValidationError(
                    _(
                        "Restrictions added make the current default values "
                        "generate an invalid configuration.\
                      \n%s"
                    )
                    % (e)
                ) from e

    def toggle_config(self):
        for record in self:
            record.config_ok = not record.config_ok

    def _create_variant_ids(self):
        """Prevent configurable products from creating variants as these serve
        only as a template for the product configurator"""
        templates = self.filtered(lambda t: not t.config_ok)
        if not templates:
            return None
        return super(ProductTemplate, templates)._create_variant_ids()

    def unlink(self):
        """- Prevent the removal of configurable product templates
            from variants
        - Patch for check access rights of user(configurable products)"""
        configurable_templates = self.filtered(
            lambda template: template.config_ok)
        if configurable_templates:
            configurable_templates[:1].check_config_user_access()
        for config_template in configurable_templates:
            variant_unlink = config_template.env.context.get(
                "unlink_from_variant", False
            )
            if variant_unlink:
                self -= config_template
        res = super(ProductTemplate, self).unlink()
        return res

    def copy(self, default=None):
        """Copy restrictions, config Steps and attribute lines
        ith product template"""
        if not default:
            default = {}
        self = self.with_context(check_constraint=False)
        res = super(ProductTemplate, self).copy(default=default)

        # Attribute lines
        attribute_line_dict = {}
        for line in res.attribute_line_ids:
            attribute_line_dict.update({line.attribute_id.id: line.id})

        # Restrictions
        for line in self.config_line_ids:
            old_restriction = line.domain_id
            new_restriction = old_restriction.copy()
            config_line_default = {
                "product_tmpl_id": res.id,
                "domain_id": new_restriction.id,
            }
            new_attribute_line_id = attribute_line_dict.get(
                line.attribute_line_id.attribute_id.id, False
            )
            if not new_attribute_line_id:
                continue
            config_line_default.update(
                {"attribute_line_id": new_attribute_line_id})
            line.copy(config_line_default)

        # Config steps
        config_step_line_default = {"product_tmpl_id": res.id}
        for line in self.config_step_line_ids:
            new_attribute_line_ids = [
                attribute_line_dict.get(old_attr_line.attribute_id.id)
                for old_attr_line in line.attribute_line_ids
                if old_attr_line.attribute_id.id in attribute_line_dict
            ]
            if new_attribute_line_ids:
                config_step_line_default.update(
                    {"attribute_line_ids": [(6, 0, new_attribute_line_ids)]}
                )
            line.copy(config_step_line_default)
        return res

    def configure_product(self):
        """launches a product configurator wizard with a linked
        template in order to configure new product."""
        return self.with_context(product_tmpl_id_readonly=True).create_config_wizard(
            click_next=False
        )

    def create_config_wizard(
        self,
        model_name="product.configurator",
        extra_vals=None,
        click_next=True,
    ):
        """create product configuration wizard
        - return action to launch wizard
        - click on next step based on value of click_next"""
        wizard_obj = self.env[model_name]
        wizard_vals = {"product_tmpl_id": self.id}
        if extra_vals:
            wizard_vals.update(extra_vals)
        wizard = wizard_obj.create(wizard_vals)
        if click_next:
            action = wizard.action_next_step()
        else:
            wizard_obj = wizard_obj.with_context(
                wizard_model=model_name,
                allow_preset_selection=True,
            )
            action = wizard_obj.get_wizard_action(wizard=wizard)
        return action

    @api.model
    def _check_config_group_rights(self):
        """Return True/False from system parameter
        - Signals access rights needs to check or not
        :Params: return : boolean"""
        ICPSudo = self.env["ir.config_parameter"].sudo()
        manager_product_configuration_settings = ICPSudo.get_param(
            "podiatry.manager_product_configuration_settings"
        )
        return manager_product_configuration_settings

    @api.model
    def check_config_user_access(self):
        """Check user have access to perform action(create/write/delete)
        on configurable products"""
        if not self._check_config_group_rights():
            return True
        config_manager = self.env.user.has_group(
            "podiatry.group_product_configurator_manager"
        )
        user_root = self.env.ref("base.user_root")
        user_admin = self.env.ref("base.user_admin")
        if (
            config_manager
            or self.env.user.id in [user_root.id, user_admin.id]
            or self.env.su
        ):
            return True
        raise ValidationError(
            _(
                "Sorry, you are not allowed to create/change this kind of "
                "document. For more information please contact your manager."
            )
        )

    @api.model
    def create(self, vals):
        """Patch for check access rights of user(configurable products)"""
        config_ok = vals.get("config_ok", False)
        if config_ok:
            self.check_config_user_access()
        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        """Patch for check access rights of user(configurable products)"""
        change_config_ok = "config_ok" in vals
        configurable_templates = self.filtered(
            lambda template: template.config_ok)
        if change_config_ok or configurable_templates:
            self[:1].check_config_user_access()

        return super(ProductTemplate, self).write(vals)

    @api.constrains("config_line_ids")
    def _check_config_line_domain(self):
        attribute_line_ids = self.attribute_line_ids
        tmpl_value_ids = attribute_line_ids.mapped("value_ids")
        tmpl_attribute_ids = attribute_line_ids.mapped("attribute_id")
        error_message = False
        for domain_id in self.config_line_ids.mapped("domain_id"):
            domain_attr_ids = domain_id.domain_line_ids.mapped("attribute_id")
            domain_value_ids = domain_id.domain_line_ids.mapped("value_ids")
            invalid_value_ids = domain_value_ids - tmpl_value_ids
            invalid_attribute_ids = domain_attr_ids - tmpl_attribute_ids
            if not invalid_value_ids and not invalid_value_ids:
                continue
            if not error_message:
                error_message = _(
                    "Following Attribute/Value from restriction "
                    "are not present in template attributes/values. "
                    "Please make sure you are adding right restriction"
                )
            error_message += _("\nRestriction: %s") % (domain_id.name)
            error_message += (
                invalid_attribute_ids
                and _("\nAttribute/s: %s")
                % (", ".join(invalid_attribute_ids.mapped("name")))
                or ""
            )
            error_message += (
                invalid_value_ids
                and _("\nValue/s: %s\n") % (", ".join(invalid_value_ids.mapped("name")))
                or ""
            )
        if error_message:
            raise ValidationError(error_message)

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        domain = args or []
        domain += ["|", ("name", operator, name),
                   ("default_code", operator, name)]
        return self.search(domain, limit=limit).name_get()

class ProductTemplateWithWeightInKg(models.Model):
    """Rename the field weight to `Weight in Kg`."""

    _inherit = 'product.template'

    weight = fields.Float(string='Weight in Kg')

class ProductTemplateWithWeightInUoM(models.Model):
    """Add the fields weight_in_uom and specific_weight_uom_id to products."""

    _inherit = 'product.template'

    weight_in_uom = fields.Float(
        related='product_variant_ids.weight_in_uom',
        readonly=False,
        store=True,
    )

    specific_weight_uom_id = fields.Many2one(
        related='product_variant_ids.specific_weight_uom_id',
        readonly=False,
        store=True,
    )

class ProductTemplateWithDimensions(models.Model):
    """Add dimension fields to products."""

    _inherit = 'product.template'

    height = fields.Float(
        related='product_variant_ids.height',
        readonly=False,
        store=True,
    )

    length = fields.Float(
        related='product_variant_ids.length',
        readonly=False,
        store=True,
    )

    width = fields.Float(
        related='product_variant_ids.width',
        readonly=False,
        store=True,
    )

    dimension_uom_id = fields.Many2one(
        related='product_variant_ids.dimension_uom_id',
        readonly=False,
        store=True,
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

    volume = fields.Float(
        related='product_variant_ids.volume',
        store=True,
    )

class ProductTemplateWithDensity(models.Model):
    """Add the field density to products."""

    _inherit = 'product.template'

    density = fields.Float(
        'Density',
        related='product_variant_ids.density',
        store=True,
    )
