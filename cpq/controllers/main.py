from odoo import _, models
from odoo.exceptions import UserError
from odoo.http import Controller, request, route

import logging
import json

_logger = logging.getLogger(__name__)

class ProductConfiguratorController(Controller):

    def _cpq_extract_from_combination(self, product_tmpl_id, combination):
        ptav_ids = request.env["product.template.attribute.value"].sudo()
        custom_dict = {}

        valid_ptav_ids = product_tmpl_id.valid_product_template_attribute_line_ids.mapped("product_template_value_ids")
        valid_ids_set = set(valid_ptav_ids.ids)

        if any(side in combination for side in ("left", "right")):
            flat_combination = {}
            for side in ("left", "right"):
                side_vals = combination.get(side)
                if isinstance(side_vals, dict):
                    flat_combination.update(side_vals)
        else:
            flat_combination = combination

        for key, val in flat_combination.items():
            try:
                ptav_id_int = int(key)
            except ValueError:
                continue

            if ptav_id_int not in valid_ids_set:
                continue

            ptav_id = valid_ptav_ids.filtered(lambda ptav: ptav.id == ptav_id_int)
            if not ptav_id:
                continue

            ptav_id.ensure_one()
            ptav_ids |= ptav_id

            if ptav_id.is_custom:
                custom_dict[ptav_id] = val

        return ptav_ids, custom_dict

    @route("/cpq/<int:product_tmpl_id>/data", type="json", auth="user")
    def cpq_tmpl_data(self, product_tmpl_id, company_id=None, pricelist_id=None, ptav_ids=None):
        product_tmpl_id = request.env["product.template"].browse(product_tmpl_id)
        if not product_tmpl_id.cpq_ok:
            raise UserError(_("Not a CPQ enabled product!"))

        return {
            "product_tmpl_id": {
                "id": product_tmpl_id.id,
                "name": product_tmpl_id.name,
                "display_name": product_tmpl_id.display_name,
                "list_price": product_tmpl_id.list_price,
                "cpq_ref": product_tmpl_id.cpq_ref,
                "description_sale": product_tmpl_id.description_sale,
            },
            "ptal_ids": product_tmpl_id.valid_product_template_attribute_line_ids._cpq_get_combination_info_list(),
        }

    @route("/cpq/<int:product_tmpl_id>/validate", type="json", auth="user")
    def cpq_validate(self, product_tmpl_id, combination):
        product_tmpl_id = request.env["product.template"].sudo().browse(product_tmpl_id)
        if not product_tmpl_id.cpq_ok:
            return {"valid": False, "msg": _("Not CPQ Enabled!")}

        ptav_ids, custom_dict = self._cpq_extract_from_combination(product_tmpl_id, combination)
        variant_ok, msg = product_tmpl_id._cpq_ensure_valid_values(
            ptav_ids, custom_dict, raise_on_invalidity=False, validate_only=True
        )

        return {"valid": variant_ok, "errors": msg}

    @route("/cpq/<int:product_tmpl_id>/configure", type="json", auth="user")
    def cpq_configure(self, product_tmpl_id, configuration):
        product_tmpl = request.env["product.template"].sudo().browse(product_tmpl_id)
        if not product_tmpl or not product_tmpl.exists():
            raise UserError(_("Product template not found."))

        if not product_tmpl.cpq_ok:
            raise UserError(_("Not a CPQ enabled product!"))

        product_id = product_tmpl.product_variant_id.id or request.env["product.product"].search([], limit=1).id

        laterality = (configuration or {}).get("laterality", "unspecified")
        selected = (configuration or {}).get("selected", {})
        split = (configuration or {}).get("split", False)
        laterality_label = laterality.capitalize()

        try:
            config_json = json.dumps({
                "laterality": laterality,
                "split": split,
                "selected": selected,
            })
        except Exception as e:
            raise UserError(_("Unable to serialize configuration: %s") % str(e))

        config_data = {
            "product_id": product_id,
            "name": f"{product_tmpl.name} - {laterality_label}",
            "cpq_configuration_json": config_json,
        }

        return {
            "product_tmpl_id": product_tmpl.id,
            "sale_order_line_id": None,
            "configuration": config_data,
        }

# Helper extension for attribute lines
class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    def _cpq_get_combination_info_list(self):
        return [line._cpq_get_combination_info() for line in self]



# import logging
# from odoo import _
# from odoo.exceptions import UserError
# from odoo.http import Controller, request, route
# import json

# _logger = logging.getLogger(__name__)

# class ProductConfiguratorController(Controller):

#     def _cpq_extract_from_combination(self, product_tmpl_id, combination):
#         """Extract ptav_ids and custom values from a given selection dict.

#         Handles both flat and bilateral ('left'/'right') combinations.
#         """
#         _logger.debug("🔍 Extracting combination for template ID %s: %s", product_tmpl_id.id, combination)

#         ptav_ids = request.env["product.template.attribute.value"].sudo()
#         custom_dict = {}

#         valid_ptav_ids = product_tmpl_id.valid_product_template_attribute_line_ids.mapped("product_template_value_ids")
#         valid_ids_set = set(valid_ptav_ids.ids)
#         _logger.debug("✅ Valid ptav_ids for this template: %s", list(valid_ids_set))

#         # Flatten structure if in bilateral format
#         if any(side in combination for side in ("left", "right")):
#             flat_combination = {}
#             for side in ("left", "right"):
#                 side_vals = combination.get(side)
#                 if isinstance(side_vals, dict):
#                     _logger.debug("🔄 Flattening %s side: %s", side, side_vals)
#                     flat_combination.update(side_vals)
#                 else:
#                     _logger.warning("⚠️ Expected dict for side '%s' but got %s", side, type(side_vals))
#         else:
#             flat_combination = combination

#         for key, val in flat_combination.items():
#             try:
#                 ptav_id_int = int(key)
#             except ValueError:
#                 _logger.debug("⏭️ Skipping non-ptav key: '%s'", key)
#                 continue

#             if ptav_id_int not in valid_ids_set:
#                 _logger.warning("⚠️ ptav_id %s not valid for this template. Skipping.", ptav_id_int)
#                 continue

#             ptav_id = valid_ptav_ids.filtered(lambda ptav: ptav.id == ptav_id_int)
#             if not ptav_id:
#                 _logger.warning("⚠️ Could not find ptav_id=%s in filtered results. Skipping.", ptav_id_int)
#                 continue

#             ptav_id.ensure_one()
#             ptav_ids |= ptav_id

#             if ptav_id.is_custom:
#                 _logger.debug("📝 Custom value for ptav_id %s: %s", ptav_id.id, val)
#                 custom_dict[ptav_id] = val
#             else:
#                 _logger.debug("✔️ Selected ptav_id %s", ptav_id.id)

#         _logger.info("✅ Extracted %d ptav_ids and %d custom values", len(ptav_ids), len(custom_dict))
#         return ptav_ids, custom_dict

#     @route("/cpq/<int:product_tmpl_id>/data", type="json", auth="user")
#     def cpq_tmpl_data(
#         self,
#         product_tmpl_id,
#         company_id=None,
#         pricelist_id=None,
#         ptav_ids=None,
#     ):
#         product_tmpl_id = request.env["product.template"].browse(product_tmpl_id)
#         if not product_tmpl_id.cpq_ok:
#             raise UserError(_("Not a CPQ enabled product!"))

#         return product_tmpl_id._cpq_get_combination_info()

#     @route("/cpq/<int:product_tmpl_id>/validate", type="json", auth="user")
#     def cpq_validate(
#         self,
#         product_tmpl_id,
#         combination,
#     ):
#         product_tmpl_id = request.env["product.template"].sudo().browse(product_tmpl_id)
#         if not product_tmpl_id.cpq_ok:
#             return {
#                 "valid": False,
#                 "msg": _("Not CPQ Enabled!"),
#             }

#         (ptav_ids, custom_dict) = self._cpq_extract_from_combination(
#             product_tmpl_id, combination
#         )

#         (variant_ok, msg) = product_tmpl_id._cpq_ensure_valid_values(
#             ptav_ids,
#             custom_dict,
#             raise_on_invalidity=False,
#             validate_only=True,
#         )

#         return {
#             "valid": variant_ok,
#             "errors": msg,
#         }

#     @route("/cpq/<int:product_tmpl_id>/configure", type="json", auth="user")
#     def cpq_configure(self, product_tmpl_id, configuration):
#         product_tmpl = request.env["product.template"].sudo().browse(product_tmpl_id)
#         if not product_tmpl or not product_tmpl.exists():
#             raise UserError(_("Product template not found."))

#         if not product_tmpl.cpq_ok:
#             raise UserError(_("Not a CPQ enabled product!"))

#         product_id = product_tmpl.product_variant_id.id or request.env["product.product"].search([], limit=1).id

#         laterality = (configuration or {}).get("laterality", "unspecified")
#         selected = (configuration or {}).get("selected", {})
#         split = (configuration or {}).get("split", False)

#         laterality_label = laterality.capitalize()

#         try:
#             config_json = json.dumps({
#                 "laterality": laterality,
#                 "split": split,
#                 "selected": selected,
#             })
#         except Exception as e:
#             raise UserError(_("Unable to serialize configuration: %s") % str(e))

#         config_data = {
#             "product_id": product_id,
#             "name": f"{product_tmpl.name} - {laterality_label}",
#             "cpq_configuration_json": config_json,
#         }

#         return {
#             "product_tmpl_id": product_tmpl.id,
#             "sale_order_line_id": None,
#             "configuration": config_data,
#         }

   