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
    try:
        if isinstance(raw, str):
            return json.loads(raw)
        elif isinstance(raw, dict):
            return raw
    except Exception as e:
        _logger.warning(f"CPQ config decode failed: {e}")
    return {}

def format_currency(amount, env):
    return formatLang(env, amount, currency_obj=env.user.company_id.currency_id)

def render_summary_html(env, order, config):
    if not isinstance(order, BaseModel) or order._name != "sale.order.line":
        raise ValueError("Expected a sale.order.line record in render_summary_html()")

    config = get_cpq_config_dict(config)
    laterality = config.get("laterality", "bilateral")
    split = config.get("split", False)
    selected = config.get("selected", {}) or {}
    quantity = config.get("quantity_to_make", 1)

    # def get_ptav(ptav_id):
    #     return env["product.template.attribute.value"].sudo().browse(int(ptav_id))

    def get_ptav(ptav_id):
        try:
            return env["product.template.attribute.value"].sudo().browse(int(ptav_id))
        except Exception as e:
            _logger.warning("Failed to browse PTAV ID %s: %s", ptav_id, e)
            return env["product.template.attribute.value"]


    # def get_label_and_value(ptav_id):
    #     ptav = get_ptav(ptav_id)
    #     if ptav.exists():
    #         linked_option = ptav.product_attribute_value_id.linked_option_id
    #         return (
    #             ptav.attribute_id.name,
    #             ptav.name,
    #             ptav.price_extra,
    #             linked_option.name if linked_option else None,
    #         )
    #     return str(ptav_id), str(ptav_id), 0.0, None

    def get_label_and_value(ptav_id):
        ptav = get_ptav(ptav_id)
        if ptav and ptav.exists():
            linked_option = ptav.product_attribute_value_id.linked_option_id
            return (
                ptav.attribute_id.name,
                ptav.name,
                ptav.price_extra,
                linked_option.name if linked_option else None,
            )
        _logger.warning("Skipped missing or deleted PTAV ID: %s", ptav_id)
        return str(ptav_id), "[deleted]", 0.0, None

    def render_line(attr_label, value_label, side, price, linked_option):
        label = f"{attr_label} - {side}: <b>{value_label}</b>"
        if linked_option:
            label += f" <span class='text-info'>[{linked_option}]</span>"
        label += f"<span class='float-end text-muted'>+ ${price:.2f}</span>"
        return f"<div>{label}</div>"

    lines = []
    left_total = right_total = 0.0

    # if laterality == "bilateral" and split:
    #     left = selected.get("left", {})
    #     right = selected.get("right", {})
    #     all_ptav_ids = set(left.keys()) | set(right.keys())
    #     for ptav_id in all_ptav_ids:
    #         if ptav_id in left:
    #             attr, val, price, opt = get_label_and_value(ptav_id)
    #             lines.append(render_line(attr, val, "Left", price, opt))
    #             left_total += price
    #         if ptav_id in right:
    #             attr, val, price, opt = get_label_and_value(ptav_id)
    #             lines.append(render_line(attr, val, "Right", price, opt))
    #             right_total += price
    # else:
    #     side_label = {"left": "Left", "right": "Right", "bilateral": "Bilateral"}.get(laterality, "Shared")
    #     for ptav_id, _ in selected.items():
    #         attr, val, price, opt = get_label_and_value(ptav_id)
    #         lines.append(render_line(attr, val, side_label, price, opt))
    #         if laterality == "left":
    #             left_total += price
    #         elif laterality == "right":
    #             right_total += price
    #         elif laterality == "bilateral":
    #             left_total += price
    #             right_total += price

    if laterality == "bilateral" and split:
        left = selected.get("left", {}) if isinstance(selected.get("left", {}), dict) else {}
        right = selected.get("right", {}) if isinstance(selected.get("right", {}), dict) else {}
        all_ptav_ids = set(left.keys()) | set(right.keys())
        for ptav_id in all_ptav_ids:
            if ptav_id in left:
                attr, val, price, opt = get_label_and_value(ptav_id)
                lines.append(render_line(attr, val, "Left", price, opt))
                left_total += price
            if ptav_id in right:
                attr, val, price, opt = get_label_and_value(ptav_id)
                lines.append(render_line(attr, val, "Right", price, opt))
                right_total += price
    else:
        side_label = {"left": "Left", "right": "Right", "bilateral": "Bilateral"}.get(laterality, "Shared")
        for ptav_id, _ in selected.items():
            attr, val, price, opt = get_label_and_value(ptav_id)
            lines.append(render_line(attr, val, side_label, price, opt))
            if laterality == "left":
                left_total += price
            elif laterality == "right":
                right_total += price
            elif laterality == "bilateral":
                left_total += price
                right_total += price

    # 🧮 Base Price Calculation
    unit_base_price = order.product_id.product_tmpl_id.list_price or 0.0
    base_multiplier = 2 if laterality == "bilateral" else 1
    base_price = unit_base_price * base_multiplier
    extras_total = left_total + right_total
    total = (base_price + extras_total) * quantity

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
    product_template = order_line.product_template_id
    partner = order_line.order_id.partner_id
    currency = order_line.currency_id or env.user.company_id.currency_id
    currency = currency.ensure_one()

    config_dict = get_cpq_config_dict(config)
    selected = config_dict.get("selected", config_dict) or {}
    config_dict["selected"] = selected 

    quantity = config_dict.get("quantity_to_make", 1)
    laterality = config_dict.get("laterality", "bilateral")
    split = config_dict.get("split", False)
    
    # Extract all PTAV IDs from the configuration
    if laterality == "bilateral" and split:
        ptav_ids = [int(pid) for side in ("left", "right") for pid in selected.get(side, {}).keys() if str(pid).isdigit()]
    else:
        ptav_ids = [int(pid) for pid in selected.keys() if str(pid).isdigit()]

    # if laterality == "bilateral" and split:
    #     ptav_ids = [int(pid) for side in ("left", "right") for pid in selected.get(side, {}).keys()]
    # else:
    #     ptav_ids = [int(pid) for pid in selected.keys() if str(pid).isdigit()]


    ptav_model = env["product.template.attribute.value"].sudo()
    ptavs = ptav_model.browse(ptav_ids).filtered(lambda p: p.exists())

    invalid_ids = [pid for pid in ptav_ids if not ptav_model.browse(pid).exists()]
    if invalid_ids:
        _logger.warning("⚠️ Skipping deleted or invalid PTAV IDs: %s", invalid_ids)

    # Check for matrix override
    matrix = env["cpq.price.matrix"].sudo()
    candidate_matrices = matrix.search([
    ("product_tmpl_id", "=", product_template.id),
    ])
    # matrix_record = candidate_matrices.filtered(
    #     lambda rec: set(rec.ptav_ids.ids).issubset(set(config["ptav_ids"]))
    # )
    matrix_record = candidate_matrices.filtered(
        lambda rec: set(rec.ptav_ids.ids).issubset(set(ptav_ids))
    )


    if matrix_record:
        matrix_price = matrix_record.price_total
        final_price = currency.round(matrix_price * quantity)

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
            "from_matrix": bool(matrix_price), 
        }

    # ⛳️ Fallback: manual price breakdown
    base_price = product_template.list_price or 0.0
    base_multiplier = 2 if laterality == "bilateral" else 1
    raw_base = base_price * base_multiplier

    # ptavs = env["product.template.attribute.value"].sudo().browse(ptav_ids)

    # ptavs = env["product.template.attribute.value"].sudo().browse(ptav_ids).filtered(lambda p: p.exists())
    # invalid_ids = [pid for pid in ptav_ids if not env["product.template.attribute.value"].browse(pid).exists()]
    # if invalid_ids:
    #     _logger.warning("Skipping deleted or invalid PTAV IDs during price breakdown: %s", invalid_ids)


    left_total = 0.0
    right_total = 0.0

    for ptav in ptavs:
        ptav_id = str(ptav.id)
        if laterality == "bilateral" and split:
            if ptav_id in selected.get("left", {}):
                left_total += ptav.price_extra
            if ptav_id in selected.get("right", {}):
                right_total += ptav.price_extra
        elif laterality == "left":
            left_total += ptav.price_extra
        elif laterality == "right":
            right_total += ptav.price_extra
        elif laterality == "bilateral":
            # Shared bilateral: both sides get the same extra
            left_total += ptav.price_extra
            right_total += ptav.price_extra

    discount_factor = get_partner_discount(env, partner, product_template)
    discounted_base = raw_base * discount_factor
    extras_total = left_total + right_total
    subtotal = discounted_base + extras_total
    final_price = currency.round(subtotal * quantity)

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
    if not partner:
        return 1.0 # No discount

    # Example rule: VIP partners get 10% off
    if partner.name == "VIP Partner":
        return 0.9

    # Future: implement customer category discounting
    return 1.0

# You can expand this to support:
# pricelists
# tags
# partner categories
# volume tiers
# custom partner fields (e.g., partner.cpq_discount_pct)

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

# def sanitize_for_json(obj):
#     if isinstance(obj, dict):
#         return {
#             sanitize_for_json(k): sanitize_for_json(v)
#             for k, v in obj.items()
#             if not isinstance(k, NewId) 
#         }

#     elif isinstance(obj, list):
#         return [sanitize_for_json(i) for i in obj]

#     elif isinstance(obj, BaseModel):
#         return obj.id if obj.id else None

#     elif isinstance(obj, NewId):
#         return None

#     elif isinstance(obj, set):
#         return list(map(sanitize_for_json, obj))

#     else:
#         return obj



