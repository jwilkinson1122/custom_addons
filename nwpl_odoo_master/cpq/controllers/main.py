import logging
import json
import pprint
from pprint import pformat
import base64
from collections import defaultdict
from odoo import api, fields, models, http, _, SUPERUSER_ID
from odoo.models import NewId
from odoo.exceptions import UserError
from odoo.http import request, route
from ...pod_log.tools.db_logger import PodDBLogger 

from ..helpers.summary_helper import (
    render_summary_html, 
    compute_cpq_price_breakdown, 
    sanitize_for_json, 
    safe_int_keys,
    get_cpq_config_dict, 
    get_validated_and_original_selected,
    flatten_grouped_selection, 
    extract_cpq_ptavs,
    generate_cpq_qr_payload, 
    resolve_cpq_preferences_for_product, 
    resolve_cpq_value_from_ptav,
    enrich_selected_with_preferences, 
    split_selected_dict_by_attribute,
    normalize_grouped_to_selected,
    ensure_flattened_selected,
    env_with_context,
    ensure_env
)
from ..hooks import check_cpq_value_links, repair_cpq_attribute_links

_logger = logging.getLogger(__name__)

class ProductConfiguratorController(http.Controller):

    # ---- Main API ----
    @http.route('/cpq_product_configurator/<int:product_tmpl_id>/data', type='json', auth='user')
    def load_data(self, product_tmpl_id, **kwargs):
        _logger.info("[Custom] Load data for template ID %s", product_tmpl_id)
        ctx = request.context or {}
        partner_id = ctx.get("partner_id")
        order_id = ctx.get("order_id")

        # Resolve partner for preference lookup
        partner = None
        if partner_id:
            partner = request.env['res.partner'].browse(partner_id).commercial_partner_id
        elif order_id:
            order = request.env["sale.order"].sudo().browse(int(order_id))
            if order.exists():
                partner = order.partner_id.commercial_partner_id
        else:
            partner = request.env.user.partner_id.commercial_partner_id
        if not partner:
            raise UserError(_("Could not resolve partner for preference lookup."))

        template = request.env['product.template'].sudo().browse(product_tmpl_id)
        if not template.exists():
            raise UserError(_("Product template not found."))

        preferences = resolve_cpq_preferences_for_product(
            request.env, partner_id=partner.id, product_tmpl_id=template.id
        )
        # or keyword: resolve_cpq_preferences_for_product(odoo_env=request.env, partner_id=..., product_tmpl_id=...)

        detailed = preferences.get("detailed", [])  # [{'ptav_id': .., 'scope': .., 'note': ..}, ...]

        preferred_ids_left  = {p["ptav_id"] for p in detailed if p.get("scope") in ("left", "shared")}
        preferred_ids_right = {p["ptav_id"] for p in detailed if p.get("scope") in ("right", "shared")}
        notes_by_ptav_id    = {p["ptav_id"]: p.get("note", "") for p in detailed if p.get("note")}

        def _b64_or_none(bin_field):
            try:
                return bin_field.decode() if isinstance(bin_field, (bytes, bytearray)) else bin_field
            except Exception:
                return None

        def _image_for_ptav(ptav):
            """Return a base64 image for a PTAV using the best available source:

            1) product.attribute.value.image_128 (synced from CPQ into PAV.image_1920)
            2) linked option image (if your bridge uses product.options.image_128)
            3) CPQ value image via the virtual back-link (x_virtual_cpq_id)

            Always returns a base64 string or None.
            """
            # 1) canonical: the PAV image (Odoo will auto-derive 128 from image_1920)
            pav = getattr(ptav, "product_attribute_value_id", False)
            if pav and hasattr(pav, "image_128") and pav.image_128:
                return _b64_or_none(pav.image_128)

            # 2) linked option
            linked_opt = getattr(ptav, "linked_option_id", False)
            if linked_opt and getattr(linked_opt, "image_128", False):
                return _b64_or_none(linked_opt.image_128)

            # 3) fallback: CPQ value through virtual backlink
            virtual_id = getattr(ptav, "x_virtual_cpq_id", False)
            if virtual_id:
                try:
                    cpqv = ptav.env["cpq.attribute.value"].sudo().browse(int(virtual_id))
                    if cpqv.exists() and getattr(cpqv, "image_128", False):
                        return _b64_or_none(cpqv.image_128)
                except Exception:
                    pass

            return None



        ptal_ids = []
        for ptal in template.valid_product_template_attribute_line_ids:
            values_payload = []
            for ptav in ptal.product_template_value_ids:
                # Prefer the “virtual CPQ id” when present so preferences can match either
                pid_for_pref = getattr(ptav, "x_virtual_cpq_id", False) or ptav.id

                values_payload.append({
                    'id': ptav.id,
                    'name': ptav.name,
                    'is_custom': getattr(ptav, "is_custom", False),
                    'price_extra': ptav.price_extra,
                    'html_color': getattr(ptav, "html_color", "") or "",
                    'cpq_custom_type': getattr(ptav, "cpq_custom_type", "") or "",
                    # preference flags
                    'isPreferred': (pid_for_pref in preferred_ids_left) or (pid_for_pref in preferred_ids_right),
                    'isPreferredLeft':  (pid_for_pref in preferred_ids_left),
                    'isPreferredRight': (pid_for_pref in preferred_ids_right),
                    'note': notes_by_ptav_id.get(pid_for_pref, ""),
                    # <-- fixed: image comes from PAV / fallbacks, not PTAV
                    'image_128': _image_for_ptav(ptav),

                })

            ptal_ids.append({
                'id': ptal.id,
                'attribute_id': ptal.attribute_id.id,
                'name': ptal.attribute_id.display_name,
                'display_type': ptal.attribute_id.display_type or "radio",
                'ptav_ids': values_payload,
            })

        return {
            'product_tmpl_id': {
                'id': template.id,
                'display_name': template.display_name,
                'description_sale': template.description_sale,
                'list_price': template.list_price,
            },
            'ptal_ids': ptal_ids,
        }

    @http.route('/cpq/<int:product_tmpl_id>/validate', type='json', auth='user')
    def cpq_validate(self, product_tmpl_id, combination, **kwargs):
        context = {"allow_virtual_ptavs": True, **(kwargs.get("context") or {})}
        template = request.env["product.template"].browse(product_tmpl_id).sudo().with_context(context)
        if not template.exists() or not template.cpq_ok:
            return {"valid": False, "errors": {"general": _("Invalid Custom product.")}}
        # Do NOT flatten!
        ptav_ids, custom_dict, cleaned_selected = extract_cpq_ptavs(request.env, template, combination)
        if not ptav_ids and template.cpq_ok:
            safe_keys = safe_int_keys(combination)
            if safe_keys:
                cpq_value_ids = request.env["cpq.attribute.value"].browse(safe_keys)
                ptav_ids = template._cpq_generate_virtual_ptavs(cpq_value_ids)
            if not ptav_ids:
                return {"valid": False, "errors": {"general": _("This product could not be configured. No attribute values were selected.")}}
        valid, msg = template._cpq_ensure_valid_values(ptav_ids, custom_dict, raise_on_invalidity=False, validate_only=True)
        return sanitize_for_json({
            "valid": valid,
            "errors": msg if isinstance(msg, dict) else {"general": msg or _("Unknown error.")},
        })

    @http.route('/cpq_product_configurator/<int:product_tmpl_id>/configure', type='json', auth='user')
    def configure(self, product_tmpl_id, configuration=None, **kwargs):
        ctx = {"allow_virtual_ptavs": True, **(kwargs.get("context") or {})}
        if ctx.get("active_model") != "sale.order.line" or not ctx.get("active_id"):
            raise UserError("Invalid active model or active ID.")
        line = request.env["sale.order.line"].browse(ctx["active_id"])
        if not line.exists():
            raise UserError(_("Sale order line not found."))
        config_dict = get_cpq_config_dict(configuration) or {}
        config_dict = ensure_flattened_selected(config_dict)
        config_dict["selected"] = normalize_grouped_to_selected(config_dict)
        _logger.info("[POST-NORM] selected.left: %s", json.dumps(config_dict["selected"].get("left", {})))
        _logger.info("[POST-NORM] selected.right: %s", json.dumps(config_dict["selected"].get("right", {})))

        laterality = config_dict.get("laterality", "bilateral")
        sel = config_dict["selected"]
        if laterality == "left" and not sel.get("left"):
            sel["left"] = sel.get("shared", {}).copy()
            sel["shared"] = {}
        elif laterality == "right" and not sel.get("right"):
            sel["right"] = sel.get("shared", {}).copy()
            sel["shared"] = {}
        config_dict.setdefault("splitByAttrMap", {})
        config_dict.pop("groupedCombinationForBackend", None)
        config_dict.pop("selected_flat", None)
        config_dict = ensure_flattened_selected(config_dict)
        ptav_ids, custom_dict, orig_sel, sanitized = get_validated_and_original_selected(line.product_template_id, config_dict)
        valid, errors = line.product_template_id.with_context(allow_virtual_ptavs=True)._cpq_ensure_valid_values(ptav_ids, custom_dict, validate_only=True)
        if not valid:
            raise UserError("\n".join(errors.values()))
        prefs = resolve_cpq_preferences_for_product(
            request.env,
            partner_id=line.order_partner_id.id or line.order_id.partner_id.id,
            product_tmpl_id=line.product_template_id.id,
        )

        enriched = enrich_selected_with_preferences(orig_sel, prefs.get("detailed", []))
        ptal_map = defaultdict(list)
        for ptav in ptav_ids:
            ptal_map[ptav.attribute_id.id].append(ptav)
        ptal_ids = []
        for attr_id, ptavs in ptal_map.items():
            values = []
            for ptav in ptavs:
                pid = ptav.x_virtual_cpq_id or ptav.id
                meta = sanitized.get(str(pid), {})
                tmpl = line.product_template_id
                cpqv = tmpl.resolve_cpq_value_from_ptav(ptav) if hasattr(tmpl, "resolve_cpq_value_from_ptav") else False
                price_extra = float(cpqv.price_extra or 0.0) if cpqv and cpqv.exists() else float(ptav.price_extra or 0.0)
                values.append({
                    "id": pid,  # still CPQ id (x_virtual_cpq_id) when present
                    "name": ptav.name,
                    "price_extra": price_extra,
                    "linked_option_id": {"id": attr_id},
                    "note": meta.get("note", ""),
                    "isPreferred": meta.get("isPreferred", False) or meta.get("isPreferredLeft", False) or meta.get("isPreferredRight", False),
                    "isPreferredLeft": meta.get("isPreferredLeft", False),
                    "isPreferredRight": meta.get("isPreferredRight", False),
                })

            ptal_ids.append({
                "id": attr_id,
                "name": ptavs[0].attribute_id.name,
                "values": values,
            })

        split_map = config_dict.get("splitByAttrMap", {})
        if not split_map:
            # Try to infer splitByAttrMap from grouped and *your just-built* ptal_ids
            grouped = config_dict.get("grouped") or config_dict.get("groupedCombinationForBackend", {})
            # DO NOT overwrite ptal_ids here!
            split_map = {}
            if isinstance(grouped, dict):
                for side in ("left", "right"):
                    for pid in grouped.get(side, {}):
                        for ptal in ptal_ids: 
                            for val in ptal.get("values", []):
                                if str(val.get("id")) == str(pid):
                                    split_map[str(ptal["id"])] = True
            if split_map:
                config_dict["splitByAttrMap"] = split_map
                _logger.warning("[PATCH] Rebuilt splitByAttrMap from grouped: %s", split_map)

        needs_split = any(split_map.values())
        structured = {"left": {}, "right": {}, "shared": {}}
        if needs_split:
            split_dict = split_selected_dict_by_attribute(
                enriched, ptal_ids, split_map, laterality
            )
            left_vals = split_dict.get("left", {})
            right_vals = split_dict.get("right", {})
            shared_vals = split_dict.get("shared", {})

            for side, vals in (("left", left_vals), ("right", right_vals)):
                for pid, raw in vals.items():
                    meta = raw if isinstance(raw, dict) else {}
                    structured[side][pid] = {**meta, "value": pid}
            for pid, raw in shared_vals.items():
                meta = raw if isinstance(raw, dict) else {}
                structured["shared"][pid] = {**meta, "value": pid}
        else:
            if laterality == "bilateral":
                for pid, raw in enriched.items():
                    meta = raw if isinstance(raw, dict) else {}
                    structured["shared"][pid] = {**meta, "value": pid}
            else:
                for pid, raw in enriched.items():
                    meta = raw if isinstance(raw, dict) else {}
                    structured[laterality][pid] = {**meta, "value": pid}
        if not needs_split:
            if structured["left"] and not structured["right"]:
                laterality = "left"
            elif structured["right"] and not structured["left"]:
                laterality = "right"
        config_dict.update({
            "split": needs_split,
            "laterality": laterality,
            "selected": flatten_grouped_selection(structured),
            "grouped": structured,
            "ptal_ids": ptal_ids,
            "cpqPreferences": prefs.get("detailed", []),
        })
        # After config_dict.update({...})
        # Ensure 'selected' isn’t empty if 'grouped' contains the picks
        def _empty_buckets(s):
            return not s or all(not (s.get(k) or {}) for k in ("left", "right", "shared"))

        if _empty_buckets(config_dict.get("selected", {})) and config_dict.get("grouped"):
            config_dict["selected"] = flatten_grouped_selection(config_dict["grouped"])

        def ensure_meta(pid, m):
            if not isinstance(m, dict):
                return {"value": pid}
            m.setdefault("value", pid)
            return m
        sel = config_dict["selected"]
        for side in ("left", "right", "shared"):
            sel[side] = {pid: ensure_meta(pid, m) for pid, m in sel.get(side, {}).items()}
        config_dict["selected"] = sel
        
        _logger.warning("[CONFIGURE] selected=%s\nlaterality=%s\nsplit=%s\nsplitByAttrMap=%s\nptal_ids=%s",
                json.dumps(config_dict["selected"], indent=2),
                config_dict["laterality"],
                config_dict.get("split", False),
                json.dumps(config_dict.get("splitByAttrMap", {}), indent=2),
                json.dumps(config_dict.get("ptal_ids", []), indent=2),
            )
        
        odoo_env = request.env
        if line and line.company_id:
            odoo_env = ensure_env(odoo_env, line)
            if getattr(line, "company_id", False):
                odoo_env = env_with_context(odoo_env, allowed_company_ids=[line.company_id.id])
                
        summary_html = render_summary_html(odoo_env, line, config_dict) or ""
        breakdown = compute_cpq_price_breakdown(odoo_env, line, config_dict)
        qty = breakdown.get("quantity", 1.0)
        unit_price = breakdown.get("final_price", 0.0) / qty if qty else 0.0
        
        config_dict["ptal_ids"] = ptal_ids
        _logger.warning("[CONFIGURE] ptal_ids being saved: %s", json.dumps(ptal_ids, indent=2))

        line.write({
            "cpq_configuration_json": json.dumps(config_dict),
            "cpq_configuration_summary": summary_html,
            "product_uom_qty": qty,
            "price_unit": unit_price,
            "name": config_dict.get("name") or line.name,
        })
        return sanitize_for_json({
            "configuration": config_dict,
            "sale_order_line_id": line.id,
            "sale_order_id": line.order_id.id,
            "price_breakdown": breakdown,
            "matrix_override": breakdown.get("from_matrix", False),
        })

    @http.route('/cpq/<int:product_tmpl_id>/price_preview', type='json', auth='user')
    def cpq_price_preview(self, product_tmpl_id, configuration, context=None):
        # Normalize env + context
        odoo_env = request.env
        ctx = {**(context or {}), **(request.context or {})}

        order_id = ctx.get("active_sale_order_id")
        if not order_id:
            _logger.warning("Missing order ID in context for price preview. Context: %s", ctx)
            qty = (configuration or {}).get("quantity_to_make", 1)
            laterality = (configuration or {}).get("laterality", "bilateral")
            split = bool((configuration or {}).get("split", False))
            return {
                "price": 0.0,
                "breakdown": {
                    "base_price": 0.0,
                    "discount_factor": 1.0,
                    "quantity": qty,
                    "laterality": laterality,
                    "split": split,
                    "left": 0.0,
                    "right": 0.0,
                    "extras_total": 0.0,
                    "subtotal": 0.0,
                    "final_price": 0.0,
                    "total": 0.0,
                    "from_matrix": False,
                }
            }

        # Align company context with the order if available
        order = odoo_env['sale.order'].sudo().browse(int(order_id))
        if order.exists() and order.company_id:
            odoo_env = ensure_env(odoo_env, order)
            if getattr(order, "company_id", False):
                odoo_env = env_with_context(odoo_env, allowed_company_ids=[order.company_id.id])
                
        # Build a transient order line in the same context
        order_line = odoo_env['sale.order.line'].with_context(ctx).new({
            'order_id': order_id,
            'product_template_id': product_tmpl_id,
        })

        # Price breakdown with the normalized env
        result = compute_cpq_price_breakdown(odoo_env, order_line, configuration or {})

        return sanitize_for_json({
            "price": result.get("final_price", 0.0),
            "breakdown": result
        })

    @http.route('/cpq/qr_payload/order/<int:order_id>', type='json', auth='user')
    def cpq_order_qr_payload(self, order_id):
        Order = request.env["sale.order"].sudo().browse(order_id)
        if not Order.exists():
            return {"error": "Invalid order ID"}
        lines_data = []
        for line in Order.order_line:
            if not line.product_template_id.cpq_ok or not line.cpq_config_hash:
                continue
            lines_data.append({
                "line_id": line.id,
                "template_id": line.product_template_id.id,
                "product_name": line.product_template_id.name,
                "config_hash": line.cpq_config_hash,
                "quantity": line.product_uom_qty,
            })
        if not lines_data:
            return {"error": "No CPQ lines found for order"}
        qr_dict = {
            "type": "cpq_order",
            "version": 1,
            "order_id": Order.id,
            "customer": Order.partner_id.name,
            "date": Order.date_order.strftime("%Y-%m-%d") if Order.date_order else None,
            "lines": lines_data,
        }
        base64_payload = base64.b64encode(json.dumps(qr_dict, separators=(",", ":")).encode()).decode()
        final_payload = f"cpq://order?data={base64_payload}"
        return {"qr_payload": final_payload}

    @http.route("/cpq/config/summary", type="json", auth="user")
    def cpq_get_summary(self, config_data):
        try:
            config_dict = get_cpq_config_dict(config_data) or {}
            config_dict = ensure_flattened_selected(config_dict)
            config_dict["selected"] = normalize_grouped_to_selected(config_dict)
            _logger.info("[POST-NORM] selected.left: %s", json.dumps(config_dict["selected"].get("left", {})))
            _logger.info("[POST-NORM] selected.right: %s", json.dumps(config_dict["selected"].get("right", {})))

            for side in ("left", "right", "shared"):
                config_dict["selected"].setdefault(side, {})
            laterality = config_dict.get("laterality", "bilateral")
            sel = config_dict["selected"]
            if laterality == "left"  and not sel["left"]:
                sel["left"], sel["shared"] = sel["shared"], {}
            elif laterality == "right" and not sel["right"]:
                sel["right"], sel["shared"] = sel["shared"], {}
            grouped = split_selected_dict_by_attribute(
                config_dict["selected"],
                config_dict.get("ptal_ids", []),
                config_dict.get("splitByAttrMap", {}),
                laterality,
            )
            config_dict["grouped"] = grouped
            config_dict["selected"] = flatten_grouped_selection(grouped)
            
            _logger.warning("[SUMMARY] selected=%s\nlaterality=%s\nsplit=%s\nsplitByAttrMap=%s\nptal_ids=%s",
                json.dumps(config_dict["selected"], indent=2),
                config_dict["laterality"],
                config_dict.get("split", False),
                json.dumps(config_dict.get("splitByAttrMap", {}), indent=2),
                json.dumps(config_dict.get("ptal_ids", []), indent=2),
            )

            html = render_summary_html(request.env, None, config_dict)
            prices = compute_cpq_price_breakdown(request.env, None, config_dict)
            return {"success": True, "summary_html": html, "price_data": prices}
        except Exception:
            _logger.exception("Failed to generate summary")
            return {"success": False}

class CpqAttributeController(http.Controller):

    @http.route('/cpq/preferences/resolve', type='json', auth='user')
    def resolve_cpq_preferences(self, partner_id, product_template_id=None):
        partner = request.env['res.partner'].browse(partner_id)
        if not partner.exists():
            return {}

        return request.env['cpq.preferences.resolver'].resolve_preferences(
            partner=partner,
            user=request.env.user,
            product_tmpl=request.env['product.template'].browse(product_template_id) if product_template_id else None,
        )

    @http.route("/cpq/preferences/<int:product_tmpl_id>", type="json", auth="user")
    def get_cpq_preferences(self, product_tmpl_id, **kwargs):
        partner_id = request.env.user.partner_id.id
        product_tmpl_id = int(product_tmpl_id)

        Rule = request.env["cpq.rules.product"].sudo()
        rules = Rule.search([
            ("product_tmpl_id", "in", [False, product_tmpl_id]),
            ("active", "=", True),
            ("partner_id", "child_of", partner_id),
        ])
        for rule in rules:
            _logger.info("Rule: Partner %s (Scope=%s) | Attribute: %s → Value: %s",
                rule.partner_id.name,
                rule.scope,
                rule.attribute_id.name,
                rule.value_id.name,
            )

        return [{
            "attribute_id": rule.attribute_id.id,
            "value_id": rule.value_id.id,
            "scope": rule.scope,
            "note": rule.note,
        } for rule in rules]

    @http.route('/cpq/<int:product_template_id>/data', type='json', auth='user')
    def cpq_product_configurator_data(self, product_template_id):
        template = request.env['product.template'].browse(product_template_id)
        if not template.exists():
            raise UserError("Product template not found.")

        partner_id = request.env.context.get("partner_id") or request.env.user.partner_id.id
        user = request.env.user
        partner = request.env['res.partner'].browse(partner_id)

        resolver = request.env['cpq.preferences.resolver']
        preferences = resolver.resolve_preferences(partner=partner, user=user, product_tmpl=template)

        context_data = {
            "quantity_to_make": 1,
            "laterality": "bilateral",
            "product_template_id": product_template_id,
        }

        notes = request.env['cpq.condition.utils']
        nonproduct_notes = notes.get_active_nonproduct_notes(partner_id, context_data)
        order_notes = notes.get_active_order_notes(partner_id, context_data)
        logic_rules = notes.get_active_logic_rules(partner_id, context_data)

        return {
            "product_tmpl_id": template.read(['name', 'list_price', 'uom_id'])[0],
            "cpq_initial_config": {
                "selected": preferences,
                "laterality": "bilateral",
                "split": False,
            },
            "cpq_notes": {
                "nonproduct": nonproduct_notes,
                "order_notes": order_notes,
                "logic": logic_rules,
            },
        }
    
    @http.route('/cpq/attribute/tree/<int:product_template_id>', type='json', auth='user')
    def cpq_attribute_tree(self, product_template_id):
        template = request.env['product.template'].sudo().browse(product_template_id)
        if not template.exists():
            raise UserError("Product template not found.")

        context = request.context or {}
        partner_id = context.get('partner_id') or request.env.user.partner_id.id
        user_id = context.get('user_id') or request.env.user.id

        partner = request.env['res.partner'].browse(partner_id)
        user = request.env['res.users'].browse(user_id)
        
        resolver = request.env['cpq.preferences.resolver']
        preferences = resolver.resolve_preferences(partner=partner, user=user, product_tmpl=template)
        detailed = preferences.get("detailed", [])

        _logger.info("[TREE] Resolved preferences:\n%s", json.dumps(detailed, indent=2))

        detailed_preferred = {
            (p['attribute_id'], p['value_id']): {
                "scope": p.get('scope', ''),
                "note": p.get('note', ''),
            }
            for p in detailed
        }

        # def get_pref_key(attr_id, value):
        #     return (attr_id, value.id)
        
        def get_pref_key(attr_id, value, side=None):
            # Include 'side' in the key, or None for backward compatibility
            return (attr_id, value.id, side)

        def serialize_value(attr, val):
            # Look up both sides, fallback to shared/global
            pref_key_left = get_pref_key(attr.id, val, side="left")
            pref_key_right = get_pref_key(attr.id, val, side="right")
            pref_key_shared = get_pref_key(attr.id, val, side="shared")

            detail_left = detailed_preferred.get(pref_key_left, {})
            detail_right = detailed_preferred.get(pref_key_right, {})
            detail_shared = detailed_preferred.get(pref_key_shared, {})

            is_pref_left = bool(detail_left) or bool(detail_shared and detail_shared.get("side") in ("left", "shared"))
            is_pref_right = bool(detail_right) or bool(detail_shared and detail_shared.get("side") in ("right", "shared"))

            note_left = detail_left.get("note") or detail_shared.get("note", "")
            note_right = detail_right.get("note") or detail_shared.get("note", "")

            inherited_left = detail_left.get("scope", "") in ["global", "partner"]
            inherited_right = detail_right.get("scope", "") in ["global", "partner"]

            # Legacy/global for compatibility
            is_pref = is_pref_left or is_pref_right

            return {
                "id": val.id,
                "name": val.name,
                "price_extra": val.price_extra,
                "triggers": [child.id for child in val.triggers_child_attribute_ids],
                "children": [],
                "isPreferred": is_pref,
                "isPreferredLeft": is_pref_left,
                "isPreferredRight": is_pref_right,
                "noteLeft": note_left,
                "noteRight": note_right,
                "inheritedLeft": inherited_left,
                "inheritedRight": inherited_right,
                "linked_option_id": {"id": val.linked_option_id.id} if val.linked_option_id else None,
                "image_128": val.image_128.decode() if val.image_128 else None,
            }

        def serialize_attribute(attr):
            return {
                "id": attr.id,
                "name": attr.name,
                "is_group": attr.is_group,
                "display_type": attr.display_type,
                "required": attr.required,
                "sequence": attr.sequence,
                "values": [] if attr.is_group else [
                    serialize_value(attr, val)
                    for val in attr.value_ids.filtered(lambda v: v.active)
                ],
                "children": [
                    serialize_attribute(child)
                    for child in attr.child_ids.filtered(lambda c: c.active)
                ],
            }

        root_attrs = template.cpq_root_attribute_ids.filtered(lambda a: a.active)
        result = [serialize_attribute(attr) for attr in root_attrs]

        _logger.info("[Custom] Serialized attribute tree with preferences for template %s", template.id)
        return result

    @http.route("/cpq/dev/check_links", type="http", auth="user")
    def cpq_check_links(self):
        env = api.Environment(http.request.cr, SUPERUSER_ID, http.request.env.context)
        html = check_cpq_value_links(env)
        return http.Response(html, content_type='text/html')

    @http.route("/cpq/dev/repair_links", type="http", auth="user")
    def cpq_repair_links(self):
        env = api.Environment(http.request.cr, SUPERUSER_ID, http.request.env.context)
        result = repair_cpq_attribute_links(env)

        def list_to_html(label, values):
            if not values:
                return f"<p><b>{label}:</b> <span style='color:green'>None</span></p>"
            rows = ''.join(f"<li>{v}</li>" for v in values)
            return f"<p><b>{label}:</b></p><ul>{rows}</ul>"

        html = f"""
            <h2>Custom Repair Complete:</h2>
            <p><b>Attributes fixed:</b> {len(result['attributes_fixed'])}</p>
            <p><b>Values created:</b> {len(result['values_created'])}</p>
            <p><b>Values skipped:</b> {len(result['values_skipped_existing'])}</p>
            {list_to_html("Attributes Fixed", result['attributes_fixed'])}
            {list_to_html("Values Created", result['values_created'])}
            {list_to_html("Values Skipped", result['values_skipped_existing'])}
            <br><a href="/web#menu_id=menu_cpq_repair_tools&model=ir.ui.menu">Back</a>
        """
        return http.Response(html, content_type='text/html')

    @route("/cpq/qr_payload/<int:line_id>", type="json", auth="user")
    def cpq_qr_payload(self, line_id):
        """
        Returns a canonical QR payload URI for a given sale.order.line.
        What this does
        Accepts a line_id for any sale.order.line
        Extracts order_id, product_template_id, and cpq_config_hash
        Uses the canonical generate_cpq_qr_payload(...) helper
        Returns:{ "qr_payload": "cpq://order/1001/line/203/template/45?config=abc123&version=1" }

        """
        line = request.env["sale.order.line"].sudo().browse(line_id)
        if not line.exists():
            return {"error": "Invalid sale order line ID"}

        order_id = line.order_id.id
        template_id = line.product_template_id.id
        config_hash = line.cpq_config_hash if hasattr(line, "cpq_config_hash") else None

        payload = generate_cpq_qr_payload(order_id, line.id, template_id, config_hash=config_hash)
