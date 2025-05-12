import logging
import json
from markupsafe import Markup
from odoo.tools.translate import _
from odoo import _
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError, ValidationError
from odoo.models import BaseModel, NewId

_logger = logging.getLogger(__name__)

def get_cpq_config_dict(raw):
    if isinstance(raw, dict):
        _logger.debug("[CPQ] Using provided dict configuration.")
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                _logger.warning("[CPQ] Parsed JSON is not a dict: %s", type(parsed))
                return {}
            _logger.debug("[CPQ] Successfully parsed configuration JSON string.")
            return parsed
        except Exception as e:
            _logger.warning("[CPQ] Failed to decode config JSON string: %s", e)
            return {}
    _logger.warning("[CPQ] Unsupported configuration type: %s", type(raw))
    return {}

def format_currency(amount, env):
    return formatLang(env, amount, currency_obj=env.user.company_id.currency_id)

def rebuild_selected_dict(config):
    _logger.debug("[CPQ] Rebuilding selected dict from flat config: %s", config)
    selected = {}
    for k, v in config.items():
        try:
            ptav_id = int(k)
        except (ValueError, TypeError):
            _logger.warning("[CPQ] Skipping non-integer PTAV ID key: %s", k)
            continue
        if isinstance(v, dict) and "value" in v:
            selected[str(ptav_id)] = {
                "id": ptav_id,
                "value": v["value"],
                "cpq_custom_type": v.get("cpq_custom_type"),
            }
            _logger.debug("[CPQ] Custom input stored for PTAV %s: %s", ptav_id, selected[str(ptav_id)])
        else:
            selected[str(ptav_id)] = ptav_id
            _logger.debug("[CPQ] Normal value stored for PTAV %s", ptav_id)
    _logger.debug("[CPQ] Final rebuilt selected dict: %s", selected)
    return selected

def extract_cpq_ptavs(env, product_template, selected_dict):
    ptav_model = env["product.template.attribute.value"]
    cpq_val_model = env["cpq.attribute.value"]
    ptav_ids = ptav_model.sudo()
    custom_dict = {}

    if isinstance(selected_dict.get("left"), dict) or isinstance(selected_dict.get("right"), dict):
        combined = {**selected_dict.get("left", {}), **selected_dict.get("right", {})}
    else:
        combined = selected_dict

    _logger.debug("[CPQ] Selected dict input: %s", combined)
    _logger.debug("[CPQ] Single-side or flattened config keys: %s", list(combined.keys()))

    for key, val in combined.items():
        try:
            val_id = int(key)
        except (TypeError, ValueError):
            _logger.warning("[CPQ] Skipping non-integer key: %s", key)
            continue

        # Legacy PAV
        pav = env["product.attribute.value"].sudo().browse(val_id)
        if pav.exists():
            _logger.info("[CPQ] Skipping legacy PAV ID %s (still active)", val_id)
            continue

        # Existing PTAV
        ptav = ptav_model.browse(val_id)
        if ptav.exists() and ptav.product_tmpl_id.id == product_template.id:
            _logger.info("[CPQ] ✔️ Found existing PTAV %s (ID: %s)", ptav.name, ptav.id)
            ptav_ids |= ptav
            if ptav.is_custom:
                custom_value = val["value"] if isinstance(val, dict) and "value" in val else val
                custom_dict[ptav] = custom_value
            continue

        # CPQ fallback
        cpq_val = cpq_val_model.browse(val_id)
        _logger.debug("[CPQ] Checking CPQ value: ID=%s, name=%s, price=%.2f", cpq_val.id, cpq_val.name, cpq_val.price_extra)
        if not cpq_val.exists():
            _logger.warning("[CPQ] ❌ Could not resolve CPQ attribute value ID: %s", val_id)
            continue

        linked_attr = cpq_val.attribute_id.linked_product_attribute_id
        if not linked_attr.exists():
            _logger.warning("[CPQ] ❌ Linked product attribute not found for CPQ value ID: %s", val_id)
            continue

        # Try resolving the related product.attribute.value via linked_option_id
                # Try resolving the related product.attribute.value via linked_option_id
        pav_id = False
        if cpq_val.linked_option_id and cpq_val.linked_option_id.product_attribute_value_id:
            pav_id = cpq_val.linked_option_id.product_attribute_value_id.id
            _logger.info("[CPQ] ↪️ Using linked PAV ID %s from product.options", pav_id)
        else:
            _logger.warning("[CPQ] No linked product.attribute.value found for CPQ value ID: %s. Proceeding without it.", val_id)

        # 🛠️ Create virtual PTAV unconditionally
        virtual = ptav_model.new({
            "product_tmpl_id": product_template.id,
            "attribute_id": linked_attr.id,
            "product_attribute_value_id": pav_id or False,
        })
        virtual.price_extra = cpq_val.price_extra or 0.0
        virtual.x_virtual_cpq_id = str(cpq_val.id)

        _logger.debug("[CPQ] Virtual PTAV: attr=%s, val=%s, price=%.2f", linked_attr.name, cpq_val.name, virtual.price_extra)
        # ptav_ids |= ptav_model.browse([virtual.id])
        ptav_ids |= ptav_model.browse() + virtual


        _logger.info("[CPQ] 🪄 Created virtual PTAV (virtual ID: %s) for attribute '%s', price_extra=%.2f",
                     virtual.x_virtual_cpq_id, linked_attr.name, virtual.price_extra)

        if cpq_val.is_custom:
            custom_value = val["value"] if isinstance(val, dict) and "value" in val else val
            custom_dict[virtual] = custom_value

    for ptav in ptav_ids:
        safe_id = getattr(ptav, 'x_virtual_cpq_id', '—')
        safe_name = ptav.name or '(Unnamed)'
        _logger.debug("[CPQ] → Final PTAV: %s | id=%s | virtual_id=%s | is_virtual=%s",
                      safe_name, ptav.id, safe_id, isinstance(ptav.id, NewId))

    return ptav_ids, custom_dict

def generate_virtual_ptavs_from_cpq(env, product_tmpl, cpq_value_ids):
    PTAV = env['product.template.attribute.value']
    ProductAttr = env['product.attribute']
    ProductAttrVal = env['product.attribute.value']

    virtual_ptavs = PTAV.browse()
    for cpq_val in cpq_value_ids:
        _logger.debug("[GEN] Processing CPQ value: %s (ID: %s, price=%.2f)", cpq_val.name, cpq_val.id, cpq_val.price_extra)

        if not cpq_val.exists():
            _logger.warning("⚠️ Skipping CPQ value ID %s: record not found.", cpq_val.id)
            continue

        cpq_attr = cpq_val.attribute_id
        if not cpq_attr or not cpq_attr.exists():
            _logger.warning("⚠️ Skipping CPQ value '%s' (ID: %s): missing attribute.", cpq_val.name, cpq_val.id)
            continue

        product_attr = cpq_attr.linked_product_attribute_id
        if not product_attr:
            product_attr = ProductAttr.create({
                "name": cpq_attr.name,
                "create_variant": "no_variant",
            })
            cpq_attr.linked_product_attribute_id = product_attr
            _logger.info("🔗 Created product.attribute '%s' for CPQ attribute ID %s", product_attr.name, cpq_attr.id)

        pav = ProductAttrVal.search([
            ("name", "=", cpq_val.name),
            ("attribute_id", "=", product_attr.id),
        ], limit=1)

        if not pav:
            _logger.warning("[GEN] ❌ No PAV found for CPQ value: %s (ID: %s) under attribute: %s — creating PTAV with no value",
                            cpq_val.name, cpq_val.id, product_attr.name)
            pav_id = False
        else:
            pav_id = pav.id
            _logger.debug("[GEN] Found matching PAV: %s (ID: %s) for CPQ value ID: %s", pav.name, pav.id, cpq_val.id)

        virtual_ptav = PTAV.new({
            "product_tmpl_id": product_tmpl.id,
            "attribute_id": product_attr.id,
            "product_attribute_value_id": pav_id,
        })
        virtual_ptav.price_extra = cpq_val.price_extra or 0.0
        virtual_ptav.x_virtual_cpq_id = str(cpq_val.id)
        virtual_ptavs += virtual_ptav
        _logger.info("[GEN] 🪄 Created virtual PTAV: attr=%s, value=%s, price=%.2f, x_virtual_cpq_id=%s",
                     product_attr.name, cpq_val.name, cpq_val.price_extra, cpq_val.id)

    return virtual_ptavs

def render_summary_html(env, order, config):
    if not isinstance(order, BaseModel) or order._name != "sale.order.line":
        raise ValueError("Expected a sale.order.line record in render_summary_html()")

    _logger.debug("[CPQ] Starting summary rendering for order line: %s", order.id)
    config = get_cpq_config_dict(config)
    _logger.debug("[CPQ] get_cpq_config_dict() input: %s", config)

    _logger.debug("[CPQ] Parsed config: %s", json.dumps(config, indent=2))

    laterality = config.get("laterality", "bilateral")
    split = config.get("split", False)
    selected = config.get("selected") or rebuild_selected_dict(config)
    quantity = config.get("quantity_to_make", 1)

    _logger.debug("[CPQ] Summary config - laterality: %s, split: %s, quantity: %s", laterality, split, quantity)
    _logger.debug("[CPQ] Selected dict: %s", json.dumps(selected, indent=2))

    ptavs, _ = extract_cpq_ptavs(env, order.product_template_id, selected)
    _logger.debug("[CPQ] Extracted PTAVs: %s", [
        f"{p.name} (id={p.id}, virtual={isinstance(p.id, NewId)}, price={p.price_extra})" for p in ptavs
    ])

    def get_label_and_value(ptav):
        if ptav and ptav.exists():
            try:
                pav = ptav.product_attribute_value_id
                linked_option = None
                if pav and pav.exists():
                    linked_option = pav.linked_option_id if pav.linked_option_id and pav.linked_option_id.exists() else None
                # Use ptav.name fallback if no PAV
                value_label = ptav.name or pav.name if pav else "(unnamed)"
                return (
                    ptav.attribute_id.name,
                    value_label,
                    ptav.price_extra,
                    linked_option.name if linked_option else None,
                )
            except Exception as e:
                _logger.warning("[CPQ] Failed to read PTAV %s: %s", ptav.id, e)
        return str(getattr(ptav, "id", "n/a")), "[deleted]", 0.0, None


    # def get_label_and_value(ptav):
    #     if ptav and ptav.exists():
    #         try:
    #             pav = ptav.product_attribute_value_id
    #             linked_option = None
    #             if pav and pav.exists():
    #                 linked_option = pav.linked_option_id if pav.linked_option_id and pav.linked_option_id.exists() else None
    #             return (
    #                 ptav.attribute_id.name,
    #                 ptav.name,
    #                 ptav.price_extra,
    #                 linked_option.name if linked_option else None,
    #             )
    #         except Exception as e:
    #             _logger.warning("[CPQ] Failed to read PTAV %s: %s", ptav.id, e)
    #     return str(getattr(ptav, "id", "n/a")), "[deleted]", 0.0, None

    def render_line(attr_label, value_label, side, price, linked_option):
        label = f"{attr_label} - {side}: <b>{value_label}</b>"
        if linked_option:
            label += f" <span class='text-info'>[{linked_option}]</span>"
        label += f"<span class='float-end text-muted'>+ ${price:.2f}</span>"
        return f"<div>{label}</div>"

    lines = []
    left_total = right_total = 0.0
    if laterality == "bilateral" and split:
        left_ids = selected.get("left", {}) if isinstance(selected.get("left"), dict) else {}
        right_ids = selected.get("right", {}) if isinstance(selected.get("right"), dict) else {}
        _logger.debug("[CPQ] Split mode active — left_ids: %s | right_ids: %s", left_ids.keys(), right_ids.keys())
        for ptav in ptavs:
            # ptav_id = getattr(ptav, "x_virtual_cpq_id", None) or str(ptav.id)
            ptav_id = ptav.x_virtual_cpq_id if hasattr(ptav, "x_virtual_cpq_id") else str(ptav.id)
            _logger.debug("[CPQ] Matching PTAV ID: %s (x_virtual_cpq_id=%s, id=%s)", ptav, getattr(ptav, "x_virtual_cpq_id", None), ptav.id)

            if not ptav_id or ptav_id == "None":
                _logger.debug("[CPQ] Skipping invalid PTAV (no ID): %s", ptav)
                continue
            if ptav_id in left_ids:
                attr, val, price, opt = get_label_and_value(ptav)
                _logger.debug("[CPQ] Adding to LEFT: %s (%s) +$%.2f", attr, val, price)
                lines.append(render_line(attr, val, "Left", price, opt))
                left_total += price
            if ptav_id in right_ids:
                attr, val, price, opt = get_label_and_value(ptav)
                _logger.debug("[CPQ] Adding to RIGHT: %s (%s) +$%.2f", attr, val, price)
                lines.append(render_line(attr, val, "Right", price, opt))
                right_total += price
    else:
        side_label = {"left": "Left", "right": "Right", "bilateral": "Bilateral"}.get(laterality, "Shared")
        _logger.debug("[CPQ] Non-split mode, rendering with side label: %s", side_label)
        for ptav in ptavs:
            attr, val, price, opt = get_label_and_value(ptav)
            _logger.debug("[CPQ] Adding to %s: %s (%s) +$%.2f", side_label, attr, val, price)
            lines.append(render_line(attr, val, side_label, price, opt))
            if laterality == "left":
                left_total += price
            elif laterality == "right":
                right_total += price
            elif laterality == "bilateral":
                left_total += price
                right_total += price

    unit_base_price = order.product_id.product_tmpl_id.list_price or 0.0
    base_multiplier = 2 if laterality == "bilateral" else 1
    base_price = unit_base_price * base_multiplier
    extras_total = left_total + right_total
    total = (base_price + extras_total) * quantity

    _logger.debug("[CPQ] Summary totals — Base: %.2f, Left: %.2f, Right: %.2f, Extras: %.2f, Total: %.2f",
        base_price, left_total, right_total, extras_total, total)

    breakdown_note = f"(${unit_base_price:.2f} x {base_multiplier})"
    price_block = f"""
        <div class="cpq-summary-card mt-2">
            {'<div><b>🦶 Left Extras:</b> $%.2f</div>' % left_total if left_total else ''}
            {'<div><b>🦶 Right Extras:</b> $%.2f</div>' % right_total if right_total else ''}
            <div><b>💵 Base:</b> ${base_price:.2f} <span class='text-muted'>{breakdown_note}</span></div>
            <div><b>➕ Extras:</b> ${extras_total:.2f}</div>
            <div><b>📊 Total (x{quantity}):</b> <b>${total:.2f}</b></div>
        </div>
    """
    return Markup(f"""<div class='cpq-summary-card'>{''.join(lines)}{price_block}</div>""")

def render_summary_plaintext(env, order, config):
    html = render_summary_html(env, order, config)
    return Markup(html).striptags()

def compute_cpq_price_breakdown(env, order_line, config):
    _logger.debug("[CPQ] Computing price breakdown for line %s", order_line.id)

    product_template = order_line.product_template_id
    partner = order_line.order_id.partner_id
    currency = order_line.currency_id or env.user.company_id.currency_id
    currency = currency.ensure_one()

    config_dict = get_cpq_config_dict(config)
    selected = config_dict.get("selected")
    if not selected:
        selected = rebuild_selected_dict(config_dict)
        _logger.warning("[CPQ] Rebuilt selected dict from flat config: %s", selected)
    config_dict["selected"] = selected

    quantity = config_dict.get("quantity_to_make", 1)
    laterality = config_dict.get("laterality", "bilateral")
    split = config_dict.get("split", False)

    _logger.debug("[CPQ] Parsed config: laterality=%s, split=%s, quantity=%s", laterality, split, quantity)
    _logger.debug("[CPQ] Selected dict: %s", json.dumps(selected, indent=2))

    ptavs, _ = extract_cpq_ptavs(env, product_template, selected)
    ptav_ids = [p.id for p in ptavs if p.id or isinstance(p.id, NewId)]

    _logger.debug("[CPQ] Final valid PTAVs:")
    for p in ptavs:
        _logger.debug(" - %s (ID: %s, price_extra=%.2f, virtual=%s)", p.name, p.id, p.price_extra, isinstance(p.id, NewId))

    # ✅ Matrix override
    matrix = env["cpq.price.matrix"].sudo()
    candidate_matrices = matrix.search([("product_tmpl_id", "=", product_template.id)])
    matrix_record = candidate_matrices.filtered(
        lambda rec: set(rec.ptav_ids.ids).issubset(set(ptav_ids))
    )
    if matrix_record:
        matrix_price = matrix_record.price_total
        final_price = currency.round(matrix_price * quantity)
        _logger.info("[CPQ] Matrix price matched: %.2f x %d = %.2f", matrix_price, quantity, final_price)

        return {
            "base_price": 0.0,
            "discount_factor": 1.0,
            "quantity": quantity,
            "laterality": laterality,
            "split": split,
            "left": 0.0,
            "right": 0.0,
            "extras_total": 0.0,
            "subtotal": matrix_price,
            "final_price": final_price,
            "total": final_price,
            "from_matrix": True,
        }

    # ⛳️ Fallback: manual price breakdown
    base_price = product_template.list_price or 0.0
    base_multiplier = 2 if laterality == "bilateral" else 1
    raw_base = base_price * base_multiplier

    left_total = 0.0
    right_total = 0.0

    for ptav in ptavs:
        # ptav_id = getattr(ptav, "x_virtual_cpq_id", None) or str(ptav.id)
        ptav_id = ptav.x_virtual_cpq_id if hasattr(ptav, "x_virtual_cpq_id") else str(ptav.id)
        _logger.debug("[CPQ] Matching PTAV ID: %s (x_virtual_cpq_id=%s, id=%s)", ptav, getattr(ptav, "x_virtual_cpq_id", None), ptav.id)

        if not ptav_id or ptav_id == "None":
            _logger.debug("[CPQ] Skipping invalid PTAV: %s", ptav)
            continue

        if laterality == "bilateral" and split:
            if ptav_id in selected.get("left", {}):
                _logger.debug("[CPQ] Adding to LEFT: %s (ID: %s) +$%.2f", ptav.name, ptav_id, ptav.price_extra)
                left_total += ptav.price_extra
            if ptav_id in selected.get("right", {}):
                _logger.debug("[CPQ] Adding to RIGHT: %s (ID: %s) +$%.2f", ptav.name, ptav_id, ptav.price_extra)
                right_total += ptav.price_extra
        elif laterality == "left":
            _logger.debug("[CPQ] Adding to LEFT (non-split): %s (ID: %s) +$%.2f", ptav.name, ptav_id, ptav.price_extra)
            left_total += ptav.price_extra
        elif laterality == "right":
            _logger.debug("[CPQ] Adding to RIGHT (non-split): %s (ID: %s) +$%.2f", ptav.name, ptav_id, ptav.price_extra)
            right_total += ptav.price_extra
        elif laterality == "bilateral":
            _logger.debug("[CPQ] Adding to BOTH: %s (ID: %s) +$%.2f", ptav.name, ptav_id, ptav.price_extra)
            left_total += ptav.price_extra
            right_total += ptav.price_extra

    discount_factor = get_partner_discount(env, partner, product_template)
    discounted_base = raw_base * discount_factor
    extras_total = left_total + right_total
    subtotal = discounted_base + extras_total
    final_price = currency.round(subtotal * quantity)

    _logger.debug("[CPQ] Final Totals — Base: %.2f, Left: %.2f, Right: %.2f, Extras: %.2f, Discount Factor: %.2f, Final Price: %.2f",
        raw_base, left_total, right_total, extras_total, discount_factor, final_price)

    return {
        "base_price": round(raw_base, 2),
        "discount_factor": discount_factor,
        "quantity": quantity,
        "laterality": laterality,
        "split": split,
        "left": round(left_total * quantity, 2),
        "right": round(right_total * quantity, 2),
        "extras_total": round(extras_total * quantity, 2),
        "subtotal": round(subtotal, 2),
        "final_price": final_price,
        "total": final_price,
        "from_matrix": False,
    }

def get_partner_discount(env, partner, template):
    # Expand this to support: pricelists, tags, partner categories, volume tiers, custom partner fields (e.g., partner.cpq_discount_pct)
    if not partner:
        return 1.0 # No discount

    # Example rule: VIP partners get 10% off
    if partner.name == "VIP Partner":
        return 0.9

    # Future: implement customer category discounting
    return 1.0

def sanitize_for_json(value, depth=0, max_depth=20):
    """Recursively sanitize a Python object for JSON serialization."""
    if depth > max_depth:
        return "..."  # Prevent infinite recursion

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, BaseModel):
        return value.id

    if isinstance(value, dict):
        return {
            sanitize_for_json(k, depth + 1): sanitize_for_json(v, depth + 1)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [sanitize_for_json(v, depth + 1) for v in value]

    if hasattr(value, "id"):
        return getattr(value, "id")

    return str(value)  # Fallback for unknown types


