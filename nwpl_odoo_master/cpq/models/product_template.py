import copy
import logging
import json

_logger = logging.getLogger(__name__)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import (
    format_amount,
    format_date,
    format_datetime,
    format_duration,
    format_time,
    is_html_empty,
)
from odoo.tools.rendering_tools import (
    parse_inline_template,
    render_inline_template,
    template_env_globals,
)
from odoo.tools.safe_eval import safe_eval

from ..helpers.summary_helper import (
    generate_virtual_ptavs_from_cpq,
    resolve_cpq_value_from_ptav as resolve_cpq_value_from_ptav_fn,
    resolve_cpq_value_from_ptav_model
)

DEFAULT_CPQ_REF_CODE = """# Available variables:
#   record: The current product.product which has been created
#   tmpl: The current product.template
#
# Output:
#   ref: Set with what you want for your end variant internal reference

ref = ""
"""

class ProductTemplate(models.Model):
    _inherit = ["multi.company.abstract", "product.template"]
    _name = "product.template"
    
    cpq_ok = fields.Boolean(string="Custom Product", default=False)

    cpq_ref = fields.Char(
        string="Custom Internal Reference",
        index=True,
        help="Reference for this configurable template",
    )

    cpq_ref_mode = fields.Selection(
        [
            ("none", "No"),
            ("inline", "Using Inline QWeb"),
            ("code", "Using Python Code"),
        ],
        default="inline",
        required=True,
        string="Dynamic Custom Variant Internal Reference",
    )

    cpq_ref_tmpl = fields.Text(
        string="Custom Internal Reference Inline QWeb Template",
        help="Inline QWeb Template for generating dynamic variant internal reference",
    )

    cpq_ref_code = fields.Text(
        default=DEFAULT_CPQ_REF_CODE,
        string="Custom Internal Reference using Python Code",
        help="Code for generating dynamic variant internal reference",
    )

    cpq_tooltip = fields.Html(compute="_compute_cpq_tooltip")

    image_128 = fields.Image("Image 128", max_width=128, max_height=128)

    cpq_root_attribute_ids = fields.Many2many(
        "cpq.attribute",
        string="Root Custom Attributes",
        help="Top-level Custom attributes for this product template.",
        domain="[('parent_id', '=', False)]",
    )
    
    
    is_pre_configured = fields.Boolean("Pre-Configured Product", default=False)
    
    preconfigured_product_id = fields.One2many(
        "product.preconfigured", "product_template_id", "Pre-Configured Item"
    )

    no_create_variants = fields.Selection(
        [
            ("yes", "Don't create them automatically"),
            ("no", "Use Odoo's default variant management"),
            ("empty", "Use the category value"),
        ],
        string="Variant creation",
        required=True,
        default="yes",
        help="Control automatic variant creation behavior.",
    )

    # def _create_variant_ids(self):
    #     """
    #     Prevent Custom-enabled templates and those explicitly opting out
    #     from creating variants during the usual Odoo process.
    #     """
    #     templates = self.filtered(lambda t: not t.cpq_ok and t.no_create_variants != "yes")
    #     if not templates:
    #         return True
    #     return super(ProductTemplate, templates)._create_variant_ids()

    # @api.model
    # def ensure_configurator_product(self, product_tmpl_id):
    #     product_tmpl = self.sudo().browse(product_tmpl_id)

    #     if not product_tmpl.exists():
    #         raise UserError("Product template not found.")

    #     if not product_tmpl.cpq_ok:
    #         raise UserError("Only Custom-enabled templates can use configurator fallback.")

    #     product = product_tmpl._ensure_configurator_product()
    #     return {"product_id": product.id}

    # def _ensure_configurator_product(self):
    #     self.ensure_one()

    #     if not self.cpq_ok:
    #         raise UserError(_(
    #             "Cannot call _ensure_configurator_product on a non-Custom product template: %s"
    #         ) % self.display_name)

    #     Product = self.env["product.product"]
    #     product = Product.search([("product_tmpl_id", "=", self.id)], limit=1)

    #     if not product:
    #         product = Product.create({
    #             "product_tmpl_id": self.id,
    #             "name": self.name,
    #             "default_code": self._generate_cpq_default_code(),
    #             "uom_id": self.uom_id.id,
    #             "uom_po_id": self.uom_po_id.id,
    #         })
    #         _logger.info("Created fallback Custom product: %s", product)

    #     return product
    
    # def _generate_cpq_default_code(self):
    #     self.ensure_one()
    #     prefix = self.env["ir.config_parameter"].sudo().get_param("cpq.default_code_prefix", "CP-")
    #     seq = self.env["ir.sequence"].sudo().next_by_code("product.product.default_code.cpq")
    #     return f"{prefix}{seq.split('-')[-1]}"  

    # @api.model
    # def get_single_product_variant(self, template_id):
    #     product_tmpl = self.sudo().browse(template_id)
    #     return product_tmpl.get_single_product_variant_internal()

    # def get_single_product_variant_internal(self):
    #     self.ensure_one()
    #     if self.cpq_ok not in [True, False]:
    #         _logger.warning(f"cpq_ok is undefined or incorrect on template {self.id} ({self.name}) — forcing to False.")
    #         self.cpq_ok = False   

    #     _logger.info("[Custom] Returning Custom variant resolution for template %s", self.display_name)
    #     if self.cpq_ok:
    #         return {
    #             "product_id": False,
    #             "mode": "configurator",
    #             "product_name": self.name,
    #             "uom_id": self.uom_id.id,
    #             "price_unit": 0.0,
    #             "has_optional_products": False,
    #         }

    #     _logger.info("[Standard] Returning real variant for template %s", self.display_name)
    #     product = self.env['product.product'].search([('product_tmpl_id', '=', self.id)], limit=1)
    #     if not product:
    #         _logger.warning(f"Non-Custom template {self.id} ({self.name}) has no variants.")
    #         return {
    #             'product_id': False,
    #             'product_name': self.name,
    #             'uom_id': self.uom_id.id,
    #             'price_unit': 0.0,
    #             'has_optional_products': False,
    #         }

    #     partner = self.env.context.get('partner_id') and self.env['res.partner'].sudo().browse(self.env.context['partner_id'])

    #     pricelist = self.env.context.get('pricelist_id') and self.env['product.pricelist'].browse(self.env.context['pricelist_id'])

    #     price = (
    #         pricelist._get_product_price(product.with_context(uom=product.uom_id.id), 1.0, partner)
    #         if pricelist else product.lst_price
    #     )

    #     return {
    #         'product_id': [product.id, product.display_name],
    #         'product_name': product.display_name,
    #         'uom_id': product.uom_id.id,
    #         'price_unit': price or product.lst_price or 0.0,
    #         'has_optional_products': bool(product.optional_product_ids),
    #     }

    # @api.model
    # def _name_search(self, name, args=None, operator="ilike", limit=100, order=None):
    #     args = args or []
    #     domain = []
    #     if name:
    #         domain = ["|", ("cpq_ref", operator, name), ("name", operator, name)]
    #         if operator in expression.NEGATIVE_TERM_OPERATORS:
    #             domain = ["&", "!"] + domain[1:]
    #     return super()._name_search(
    #         name, expression.AND([domain, args]), operator, limit, order
    #     )

    # def _cpq_tooltip_items(self):
    #     self.ensure_one()
    #     return [
    #         _("Custom Products will generate their product variants on demand."),
    #         _(
    #             "Custom Products allow for custom inputs to be \
    #                 propagated through the system."
    #         ),
    #     ]

    # @api.depends("cpq_ok")
    # def _compute_cpq_tooltip(self):
    #     for record in self:
    #         if not record.cpq_ok:
    #             record.cpq_tooltip = False
    #             continue
    #         record.cpq_tooltip = "".join(
    #             [f"<p>{i}</p>" for i in self._cpq_tooltip_items()]
    #         )

    # @api.depends("product_variant_ids.product_tmpl_id")
    # def _compute_product_variant_count(self):
    #     """
    #     For cpq products return the number of variants configured or at least 1.

    #     Many views and methods trigger only when a template has at least
    #     one variant attached, and need them to function appropriately.
    #     """
    #     res = super()._compute_product_variant_count()
    #     for record in self.filtered(lambda p: p.cpq_ok and not p.product_variant_ids):
    #         record.product_variant_count = 1
    #     return res

    # @api.depends("cpq_ok", "product_variant_ids", "product_variant_ids.default_code")
    # def _compute_default_code(self):
    #     todo = self
    #     for record in self.filtered(lambda r: r.cpq_ok):
    #         record.default_code = False
    #         todo -= record
    #     return super(ProductTemplate, todo)._compute_default_code()

    # def _set_default_code(self):
    #     Sequence = self.env['ir.sequence']
    #     for template in self.filtered(lambda t: not t.cpq_ok):
    #         for variant in template.product_variant_ids:
    #             if not variant.default_code:
    #                 variant.default_code = Sequence.next_by_code("product.product.default_code.non_cpq")
    #     return super(ProductTemplate, self.filtered(lambda r: r.cpq_ok))._set_default_code()

    # @api.constrains('product_variant_ids')
    # def _check_unique_prefixes(self):
    #     for tmpl in self:
    #         for variant in tmpl.product_variant_ids:
    #             if variant.default_code:
    #                 if variant.default_code.startswith("CP-") and not tmpl.cpq_ok:
    #                     raise ValidationError("CP-style reference used on non-Custom product.")
    #                 if variant.default_code.startswith("P-") and tmpl.cpq_ok:
    #                     raise ValidationError("Standard reference used on Custom product.")

    # def _onchange_cpq_ok_warning_msg(self):
    #     self.ensure_one()

    #     return [
    #         "Switching a product to/from configurable when there are"
    #         " pre-existing variants will almost certainly have an unexpected"
    #         " outcome. ",
    #         "It is suggested either to archive the existing"
    #         " product and create a new one, or archive/delete all"
    #         " existing variants, unless you are 100%"
    #         " sure that you are not introducing incompatibilities"
    #         " into the system.",
    #     ]

    # @api.onchange("cpq_ok")
    # def _onchange_cpq_ok(self):
    #     if not self._origin:
    #         return

    #     if self._origin.cpq_ok != self.cpq_ok and self.product_variant_ids:
    #         return {
    #             "warning": {
    #                 "title": _("Changing Configurable is Dangerous"),
    #                 "message": _("\n\n".join(self._onchange_cpq_ok_warning_msg())),
    #             }
    #         }

    # def toggle_cpq(self):
    #     for record in self:
    #         record.cpq_ok = not record.cpq_ok

    # def configure_cpq_dialog(self):
    #     self.ensure_one()

    #     return {
    #         "name": "Custom Dialog",
    #         "type": "ir.actions.client",
    #         "tag": "cpq.ConfigureDialogAction",
    #         "target": "self",
    #     }
    
    # def _cpq_get_create_variant_vals(self, pta_value_ids, custom_dict=None):
    #     self.ensure_one()

    #     cpq_custom_values = []

    #     if not custom_dict:
    #         custom_dict = {}

    #     for ptav_id, value in custom_dict.items():
    #         cpq_custom_values.append(
    #             (
    #                 0,
    #                 0,
    #                 {
    #                     "ptav_id": ptav_id.id,
    #                     "custom_value": value,
    #                 },
    #             )
    #         )

    #     vals = {
    #         "product_tmpl_id": self.id,
    #         "product_template_attribute_value_ids": [(6, 0, pta_value_ids.ids)],
    #         "cpq_custom_value_ids": cpq_custom_values or False,
    #     }

    #     return vals
    
    # def resolve_cpq_value_from_ptav(self, ptav):
    #     return resolve_cpq_value_from_ptav_fn(ptav, env=self.env)

    # def _cpq_ensure_valid_values(
    #     self,
    #     ptav_ids,
    #     custom_dict,
    #     raise_on_invalidity=True,
    #     validate_only=False,
    # ):
    #     self.ensure_one()
    #     self = self.with_context(allow_virtual_ptavs=self.env.context.get("allow_virtual_ptavs", True))

    #     errors = {}
    #     valid = True

    #     if not self.cpq_ok:
    #         msg = _("%s is not a Custom Enabled Product!") % self.display_name
    #         _logger.warning("[INVALID] cpq_ok is False: %s", msg)
    #         if raise_on_invalidity:
    #             raise UserError(msg)
    #         return False, msg

    #     if not ptav_ids:
    #         msg = _("%s could not be configured — did not receive any product template attribute values!") % self.display_name
    #         _logger.warning("[INVALID] No PTAVs provided: %s", msg)
    #         if raise_on_invalidity:
    #             raise UserError(msg)
    #         return False, msg

    #     matched_ptav_ids = self.env["product.template.attribute.value"]

    #     for ptav in ptav_ids:
    #         pav = ptav.product_attribute_value_id
    #         ptav_key = ptav.id or getattr(ptav, "virtual_id", None) or ptav.display_name or "unknown"

    #         if not pav or not pav.exists():
    #             if not self.env.context.get("allow_virtual_ptavs"):
    #                 msg = _("Invalid PTAV: linked product attribute value is missing or deleted (PTAV ID: %s)") % (ptav.id or "virtual")
    #                 if raise_on_invalidity:
    #                     raise UserError(msg)
    #                 errors[ptav_key] = msg
    #                 valid = False
    #                 continue
    #             else:
    #                 continue

    #         if pav.is_custom:
    #             custom_value = custom_dict.get(ptav)
    #             is_valid = pav._cpq_validate_custom(custom_value)
    #             _logger.info("[DEBUG] Custom value for PTAV %s: %s (valid=%s)", ptav.display_name, custom_value, is_valid)
    #             if not self.env.context.get("skip_cpq_validate_ptav_ids") and not is_valid:
    #                 msg = _("Custom value '%(name)s' invalid: '%(value)s'") % {
    #                     "name": ptav.display_name,
    #                     "value": custom_value,
    #                 }
    #                 _logger.warning("[INVALID] Custom validation failed: %s", msg)
    #                 if raise_on_invalidity:
    #                     raise UserError(msg)
    #                 errors[ptav_key] = msg
    #                 valid = False
    #         else:
    #             cpq_val = self.resolve_cpq_value_from_ptav(ptav)
    #             is_valid = bool(cpq_val)
    #             _logger.info(
    #                 "[DEBUG] Static value for PTAV %s: %s (valid=%s)",
    #                 ptav.display_name,
    #                 (ptav.product_attribute_value_id and ptav.product_attribute_value_id.name) or "n/a",
    #                 is_valid,
    #             )
    #             if not self.env.context.get("skip_cpq_validate_ptav_ids") and not is_valid:
    #                 msg = _("Static value '%(name)s' invalid — no matching Custom value.") % {
    #                     "name": ptav.display_name,
    #                 }
    #                 _logger.warning("[INVALID] Static validation failed: %s", msg)
    #                 if raise_on_invalidity:
    #                     raise UserError(msg)
    #                 errors[ptav_key] = msg
    #                 valid = False

    #         matched_ptav_ids |= ptav

    #     if not valid and not errors:
    #         errors["general"] = _("Configuration failed validation but no specific error was returned.")

    #     if validate_only:
    #         _logger.warning("[RESULT] Validation %s with errors: %s", "failed" if not valid else "passed", errors or "None")
    #         return valid, errors

    #     if not valid:
    #         if raise_on_invalidity:
    #             raise UserError("\n".join(errors.values() or [_("Invalid configuration.")]))
    #         return False, errors or {"general": _("This configuration is not possible.")}

    #     _logger.info("[OK] Custom configuration accepted without errors.")
    #     return True, {}

    # def _cpq_generate_virtual_ptavs(self, cpq_value_ids):
    #     self.ensure_one()
    #     return generate_virtual_ptavs_from_cpq(self.env, self, cpq_value_ids)

    # def _cpq_get_create_variant(self, ptav_ids, custom_dict):
    #     self.ensure_one()
    #     (
    #         search_domain,
    #         matched_custom_dict,
    #         matched_ptav_ids,
    #         cpq_combination_indices,
    #         cpq_custom_combination_indices,
    #     ) = self._cpq_ensure_valid_values(ptav_ids, custom_dict)

    #     variant_ids = self.env["product.product"].search(search_domain)

    #     if variant_ids:
    #         variant_id = fields.first(variant_ids)
    #         return self._cpq_get_create_variant_post_find_hook(variant_id)

    #     variant_id = (
    #         self.env["product.product"]
    #         .sudo()
    #         .with_context(mail_create_nolog=True)
    #         .create(
    #             self._cpq_get_create_variant_vals(matched_ptav_ids, matched_custom_dict)
    #         )
    #     )
    #     variant_id = self._cpq_get_create_variant_post_create_hook(variant_id)
    #     variant_id.message_post(
    #         body=_("Product created via custom wizard"),
    #         author_id=self.env.user.partner_id.id,
    #     )
    #     if variant_id.cpq_combination_indices != cpq_combination_indices:
    #         raise ValidationError(
    #             _(
    #                 "Possible programming error, cpq_combination_indices"
    #                 " mismatch. Found %(found)s, expected %(expected)s"
    #             )
    #             % {
    #                 "found": variant_id.cpq_combination_indices,
    #                 "expected": cpq_combination_indices,
    #             }
    #         )

    #     if variant_id.cpq_custom_combination_indices != cpq_custom_combination_indices:
    #         raise ValidationError(
    #             _(
    #                 "Possible programming error, cpq_custom_combination_indices"
    #                 " mismatch. Found %(found)s, expected %(expected)s"
    #             )
    #             % {
    #                 "found": variant_id.cpq_custom_combination_indices,
    #                 "expected": cpq_custom_combination_indices,
    #             }
    #         )

    #     return variant_id

    # def _cpq_get_create_variant_post_find_hook(self, variant_id):
    #     return variant_id

    # def _cpq_get_variant_ref(self, variant_id):
    #     self.ensure_one()
    #     if self.cpq_ref_mode == "none":
    #         return False

    #     if self.cpq_ref_mode == "inline":
    #         return self._cpq_render_inline_template(
    #             self.cpq_ref_tmpl,
    #             extras={
    #                 "record": variant_id,
    #                 "tmpl": self,
    #             },
    #         )

    #     if self.cpq_ref_mode == "code" and self.cpq_ref_code:
    #         eval_context = {
    #             "record": variant_id,
    #             "tmpl": self,
    #         }
    #         safe_eval(
    #             self.cpq_ref_code, eval_context, mode="exec", nocopy=True
    #         )  
    #         return eval_context.get("ref")

    # def _cpq_get_create_variant_post_create_hook(self, variant_id):
    #     default_code = self._cpq_get_variant_ref(variant_id)
    #     if default_code:
    #         variant_id.default_code = default_code
    #     return variant_id

    # def _cpq_get_combination_info(self):
    #     self.ensure_one()
    #     product_tmpl_id = self

    #     return {
    #         "product_tmpl_id": {
    #             "id": product_tmpl_id.id,
    #             "name": product_tmpl_id.name,
    #             "display_name": product_tmpl_id.display_name,
    #             "cpq_ref": product_tmpl_id.cpq_ref,
    #             "description_sale": product_tmpl_id.description_sale,
    #         },
    #         "ptal_ids": [
    #             i._cpq_get_combination_info()
    #             for i in product_tmpl_id.valid_product_template_attribute_line_ids
    #         ],
    #     }

    # def _cpq_render_inline_template(self, template, extras=None):
    #     template_instructions = parse_inline_template(str(template))
    #     is_dynamic = len(template_instructions) > 1 or template_instructions[0][1]
    #     if is_dynamic:
    #         render_env = self._cpq_render_inline_template_context(extras)
    #         return render_inline_template(template_instructions, render_env)
    #     return template

    # @api.model
    # def _cpq_render_inline_template_context(self, extras=None):
    #     """
    #     Evaluation context used in all rendering engines.
    #     Contains
    #       * ``user``: current user browse record;
    #       * ``ctx```: current context;
    #       * various formatting tools;
    #     """
    #     render_context = {
    #         "format_date": lambda date, date_format=False, lang_code=False: format_date(
    #             self.env, date, date_format, lang_code
    #         ),
    #         "format_datetime": lambda dt,
    #         tz=False,
    #         dt_format=False,
    #         lang_code=False: format_datetime(self.env, dt, tz, dt_format, lang_code),
    #         "format_time": lambda time,
    #         tz=False,
    #         time_format=False,
    #         lang_code=False: format_time(self.env, time, tz, time_format, lang_code),
    #         "format_amount": lambda amount, currency, lang_code=False: format_amount(
    #             self.env, amount, currency, lang_code
    #         ),
    #         "format_duration": lambda value: format_duration(value),
    #         "user": self.env.user,
    #         "ctx": self._context,
    #         "is_html_empty": is_html_empty,
    #     }
    #     render_context.update(copy.copy(template_env_globals))

    #     if extras and isinstance(extras, dict):
    #         render_context.update(extras)

    #     return render_context
    
    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if vals.get("cpq_ok"):
    #             vals.setdefault("no_create_variants", "yes")
    #     return super().create(vals_list)

    # def write(self, vals):
    #     res = super().write(vals)
    #     if "attribute_line_ids" in vals:
    #         self._cpq_archive_impossible_configurations()
    #     return res

    # def _cpq_archive_impossible_configurations(self):
    #     archived = self.env["product.product"].with_context(active_test=False)

    #     for record in self.filtered(lambda p: p.cpq_ok):
    #         for variant in record.product_variant_ids:
    #             is_combination_possible = self._is_combination_possible_by_config(
    #                 combination=variant.product_template_attribute_value_ids,
    #                 ignore_no_variant=True,
    #             )
    #             if not is_combination_possible:
    #                 archived |= variant
    #                 variant.active = False
    #                 variant.message_post(
    #                     body=_(
    #                         "Auto-archived as no longer possible by configuration"
    #                         " (Custom) through attribute change."
    #                     )
    #                 )

    #     return archived

    # @api.model
    # def action_clean_cpq_flags(self):
    #     templates_to_fix = self.search([('cpq_ok', '=', True)])
    #     logs = []
    #     for tmpl in templates_to_fix:
    #         if not tmpl.cpq_ref and not tmpl.valid_product_template_attribute_line_ids:
    #             tmpl.cpq_ok = False
    #             logs.append(f"Disabled cpq_ok for: {tmpl.name} (ID: {tmpl.id})")
    #         else:
    #             logs.append(f"🟢 Kept cpq_ok=True for: {tmpl.name} (ID: {tmpl.id}) - cpq_ref: {tmpl.cpq_ref}, attrib lines: {tmpl.valid_product_template_attribute_line_ids.ids}")
    #     return '\n'.join(logs)
    
    # def action_add_price_matrix_line(self):
    #     self.ensure_one()
    #     return {
    #         'name': "Add Price Matrix Line",
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'cpq.price.matrix.line',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {
    #             'default_product_tmpl_id': self.id
    #         }
    #     }
    
    # def action_open_price_matrix_lines(self):
    #     self.ensure_one()
    #     return {
    #         'name': "Price Matrix for %s" % self.name,
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'cpq.price.matrix',
    #         'view_mode': 'tree,form',
    #         'domain': [('product_tmpl_id', '=', self.id)],
    #         'context': {'default_product_tmpl_id': self.id},
    #     }
