import itertools
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import config

class ProductTemplate(models.Model):
    _inherit = "product.template"

    customization_group_ids = fields.Many2many('pos.order.customization.group', string='Customization Groups')

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

    has_pending_variants = fields.Boolean(
        string="Has pending variants?",
        compute="_compute_pending_variants",
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

    @api.model_create_multi
    def create(self, vals_list):
        if "product_name" in self.env.context:
            for vals in vals_list:
                # Needed because ORM removes this value from the dictionary
                vals["name"] = self.env.context["product_name"]
        return super().create(vals_list)

    def write(self, values):
        res = super().write(values)
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

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        # Make a search with default criteria
        temp = super(models.Model, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        # Make the other search
        temp += super().name_search(
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


# class ProductTemplate(models.Model):
#     _inherit = "product.template"

#     customization_group_ids = fields.Many2many('pos.order.customization.group', string='Customization Groups')
#     no_create_variants = fields.Selection(
#         [
#             ("yes", "Don't create them automatically"),
#             ("no", "Use Odoo's default variant management"),
#             ("empty", "Use the category value"),
#         ],
#         string="Variant creation",
#         required=True,
#         default="no",
#         help="This selection defines if variants for all attribute "
#         "combinations are going to be created automatically at saving "
#         "time.",
#     )

#     @api.model_create_multi
#     def create(self, vals_list):
#         records = super().create(vals_list)
#         for i, product_tmpl in enumerate(records):
#             single_vals = vals_list[i] if isinstance(vals_list, list) else vals_list
#             product_tmpl._update_fix_price(single_vals)
#         if "product_name" in self.env.context:
#             for vals in vals_list:
#                 vals["name"] = self.env.context["product_name"]
#         return records

#     def write(self, vals):
#         res = super().write(vals)
#         if self.env.context.get("skip_update_fix_price", False):
#             return res
#         for template in self:
#             template._update_fix_price(vals)
#         if "no_create_variants" in vals:
#             self._create_variant_ids()
#         return res

#     def _update_fix_price(self, vals):
#         if "list_price" in vals:
#             self.mapped("product_variant_ids").write({"fix_price": vals["list_price"]})

#     @api.onchange("no_create_variants")
#     def onchange_no_create_variants(self):
#         if (
#             self.no_create_variants in ["no", "empty"]
#             and self._origin.no_create_variants
#         ):
#             return {
#                 "warning": {
#                     "title": _("Change warning!"),
#                     "message": _(
#                         "Changing this parameter may cause automatic variants creation"
#                     ),
#                 }
#             }

#     def _get_combination_info(
#         self,
#         combination=False,
#         product_id=False,
#         add_qty=1,
#         pricelist=False,
#         parent_combination=False,
#         only_template=False,
#     ):
#         res = super()._get_combination_info(
#             combination,
#             product_id,
#             add_qty,
#             pricelist,
#             parent_combination,
#             only_template,
#         )
#         res["price_extra"] = 0.0
#         return res

#     def _get_product_attributes_dict(self):
#         return self.attribute_line_ids.mapped(
#             lambda x: {"attribute_id": x.attribute_id.id}
#         )

#     def _create_variant_ids(self):
#         obj = self.with_context(creating_variants=True)
#         if config["test_enable"] and not self.env.context.get("check_variant_creation"):
#             return super(ProductTemplate, obj)._create_variant_ids()
#         for tmpl in obj:
#             if (
#                 (
#                     tmpl.no_create_variants == "empty"
#                     and not tmpl.categ_id.no_create_variants
#                 )
#                 or tmpl.no_create_variants == "no"
#                 or not tmpl.attribute_line_ids
#             ):
#                 super(ProductTemplate, tmpl)._create_variant_ids()
#         return True

#     @api.model
#     def name_search(self, name="", args=None, operator="ilike", limit=100):
#         temp = super(models.Model, self).name_search(
#             name=name, args=args, operator=operator, limit=limit
#         )
#         temp += super().name_search(
#             name=name, args=args, operator=operator, limit=limit
#         )
#         res = []
#         keys = []
#         for val in temp:
#             if val[0] not in keys:
#                 res.append(val)
#                 keys.append(val[0])
#                 if limit and len(res) >= limit:
#                     break
#         return res

