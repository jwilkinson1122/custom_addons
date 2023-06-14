
import itertools
from odoo import api, fields, exceptions, models, tools, _
from odoo.tools import config
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval
# product.template
class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    is_booking_order = fields.Boolean(default=False)
    is_device = fields.Boolean(string='Is Device')
    is_option = fields.Boolean(string='Is Option')
    is_custom_device = fields.Boolean(default=False, help="True if product is a brace")   
    is_otc_device = fields.Boolean(default=False, help="True if product does not require a order") 
    is_brace_device = fields.Boolean(default=False, help="True if product is a brace")  
    is_helpdesk = fields.Boolean("Helpdesk Ticket?")
    helpdesk_team = fields.Many2one('helpdesk.team', string='Helpdesk Team')
    helpdesk_assigned_to = fields.Many2one('res.users', string='Assigned to')
    
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
                
    @api.model
    def create(self, vals):
        templates = super (ProductTemplate,self).create(vals)
        if templates.product_variant_count <= 1:
            if templates.product_variant_id:
                templates.product_variant_id.is_helpdesk = templates.is_helpdesk
                templates.product_variant_id.helpdesk_team = templates.helpdesk_team.id
                templates.product_variant_id.helpdesk_assigned_to = templates.helpdesk_assigned_to.id
        return templates

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
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

    has_pending_variants = fields.Boolean(
        string="Has pending variants?",
        compute="_compute_pending_variants",
    )

    @api.depends(
        "product_variant_ids",
        "attribute_line_ids",
        "attribute_line_ids.attribute_id",
        "attribute_line_ids.value_ids",
    )
    def _compute_pending_variants(self):
        for rec in self:
            rec.has_pending_variants = bool(self._get_values_without_variant())

    def _get_values_without_variant(self):
        lines_without_no_variants = (
            self.valid_product_template_attribute_line_ids._without_no_variant_attributes()
        )
        all_variants = self.product_variant_ids.sorted(
            lambda p: (p.active, p.id and -p.id or False)
        )
        all_combinations = itertools.product(
            *[
                ptal.product_template_value_ids._only_active()
                for ptal in lines_without_no_variants
            ]
        )
        existing_variants = {
            variant.product_template_attribute_value_ids: variant
            for variant in all_variants
        }
        values_without_variant = {}
        for combination_tuple in all_combinations:
            combination = self.env["product.template.attribute.value"].concat(
                *combination_tuple
            )
            is_combination_possible = self._is_combination_possible_by_config(
                combination, ignore_no_variant=True
            )
            if not is_combination_possible:
                continue
            if combination not in existing_variants:
                for value in combination:
                    if isinstance(value.attribute_id.id, models.NewId) or isinstance(
                        value.product_attribute_value_id.id, models.NewId
                    ):
                        continue
                    values_without_variant.setdefault(
                        value.attribute_id.id,
                        {
                            "required": value.attribute_line_id.required,
                            "value_ids": [],
                        },
                    )
                    values_without_variant[value.attribute_id.id]["value_ids"].append(
                        value.product_attribute_value_id.id
                    )
        return values_without_variant

    no_create_variants = fields.Selection(
        [
            ("yes", "Don't create them automatically"),
            ("no", "Use Odoo's default variant management"),
            ("empty", "Use the category value"),
        ],
        string="Variant creation",
        required=True,
        default="no",
        help="This selection defines if variants for all attribute "
        "combinations are going to be created automatically at saving "
        "time.",
    )

    @api.onchange("no_create_variants")
    def onchange_no_create_variants(self):
        if (
            self.no_create_variants in ["no", "empty"]
            and self._origin.no_create_variants
        ):
            # the test on self._origin.no_create_variants is to
            # avoid the warning when opening a new form in create
            # mode (ie when the onchange triggers when Odoo sets
            # the default value)
            return {
                "warning": {
                    "title": _("Change warning!"),
                    "message": _(
                        "Changing this parameter may cause"
                        " automatic variants creation"
                    ),
                }
            }

    @api.model
    def create(self, vals):
        if "product_name" in self.env.context:
            # Needed because ORM removes this value from the dictionary
            vals["name"] = self.env.context["product_name"]
        return super(ProductTemplate, self).create(vals)

    def write(self, values):
        res = super(ProductTemplate, self).write(values)
        if "no_create_variants" in values:
            self._create_variant_ids()
        return res

    def _get_product_attributes_dict(self):
        return self.attribute_line_ids.mapped(
            lambda x: {"attribute_id": x.attribute_id.id}
        )

    def _create_variant_ids(self):
        obj = self.with_context(creating_variants=True)
        if config["test_enable"] and not self.env.context.get("check_variant_creation"):
            return super(ProductTemplate, obj)._create_variant_ids()
        for tmpl in obj:
            if (
                (
                    tmpl.no_create_variants == "empty"
                    and not tmpl.categ_id.no_create_variants
                )
                or tmpl.no_create_variants == "no"
                or not tmpl.attribute_line_ids
            ):
                super(ProductTemplate, tmpl)._create_variant_ids()
        return True

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        # Make a search with default criteria
        temp = super(models.Model, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        # Make the other search
        temp += super(ProductTemplate, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        # Merge both results
        res = []
        keys = []
        for val in temp:
            if val[0] not in keys:
                res.append(val)
                keys.append(val[0])
                if limit and len(res) >= limit:
                    break
        return res



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
