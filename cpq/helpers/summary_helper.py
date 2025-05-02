import logging
import json
from markupsafe import Markup
from odoo.tools.translate import _
from odoo import _
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError, ValidationError
from odoo.models import BaseModel

_logger = logging.getLogger(__name__)

def get_cpq_config_dict(raw):
    try:
        if isinstance(raw, str):
            return json.loads(raw)
        elif isinstance(raw, dict):
            return raw
    except Exception as e:
        _logger.warning(f"⚠️ CPQ config decode failed: {e}")
    return {}

def format_currency(amount, env):
    return formatLang(env, amount, currency_obj=env.user.company_id.currency_id)

def render_summary_html(env, order, config):
    if not isinstance(order, BaseModel) or order._name != "sale.order.line":
        raise ValueError("Expected a sale.order.line record in render_summary_html()")

    laterality = config.get("laterality", "bilateral")
    split = config.get("split", False)
    selected = config.get("selected", {}) or {}
    quantity = config.get("quantity_to_make", 1)

    def get_ptav(ptav_id):
        return env["product.template.attribute.value"].sudo().browse(int(ptav_id))

    def get_label_and_value(ptav_id):
        ptav = get_ptav(ptav_id)
        if ptav.exists():
            return ptav.attribute_id.name, ptav.name, ptav.price_extra
        return str(ptav_id), str(ptav_id), 0.0

    lines = []
    left_total = right_total = 0.0

    if laterality == "bilateral" and split:
        left = selected.get("left", {})
        right = selected.get("right", {})
        combined = {}

        for ptav_id in set(left.keys()).union(right.keys()):
            attr_label, _, _ = get_label_and_value(ptav_id)
            combined.setdefault(attr_label, {"left": None, "right": None, "ptav_id_left": None, "ptav_id_right": None})

            if ptav_id in left:
                _, val, price = get_label_and_value(ptav_id)
                combined[attr_label]["left"] = val
                combined[attr_label]["ptav_id_left"] = ptav_id
                left_total += price

            if ptav_id in right:
                _, val, price = get_label_and_value(ptav_id)
                combined[attr_label]["right"] = val
                combined[attr_label]["ptav_id_right"] = ptav_id
                right_total += price

        for attr_label, vals in combined.items():
            if vals["left"]:
                left_val = vals["left"]
                price = get_label_and_value(vals["ptav_id_left"])[2]
                lines.append(f"<div>{attr_label} - Left: <b>{left_val}</b> <span class='float-end text-muted'>+ ${price:.2f}</span></div>")
            if vals["right"]:
                right_val = vals["right"]
                price = get_label_and_value(vals["ptav_id_right"])[2]
                lines.append(f"<div>{attr_label} - Right: <b>{right_val}</b> <span class='float-end text-muted'>+ ${price:.2f}</span></div>")
    else:
        side_label = {"left": "Left", "right": "Right", "bilateral": "Bilateral"}.get(laterality, "Shared")
        for ptav_id, val in selected.items():
            attr_label, value_label, price = get_label_and_value(ptav_id)
            lines.append(f"<div>{attr_label} - {side_label}: <b>{value_label}</b> <span class='float-end text-muted'>+ ${price:.2f}</span></div>")
            if laterality == "left":
                left_total += price
            elif laterality == "right":
                right_total += price
            elif laterality == "bilateral":
                left_total += price
                right_total += price

    # 🧮 Base Price Calculation
    unit_base_price = order.product_id.product_tmpl_id.list_price
    base_multiplier = 2 if laterality == "bilateral" else 1
    base_price = unit_base_price * base_multiplier
    extras_total = left_total + right_total
    total = (base_price + extras_total) * quantity

    # 🧾 Price Explanation
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

    # return Markup(f"<div class='cpq-summary'>{''.join(lines)}{price_block}</div>")

def render_summary_plaintext(env, order, config):
    html = render_summary_html(env, order, config)
    return Markup(html).striptags()

def compute_cpq_price_breakdown(env, order_line, config):
    template = order_line.product_template_id
    partner = order_line.order_id.partner_id
    currency = order_line.currency_id or env.user.company_id.currency_id
    currency = currency.ensure_one()

    quantity = config.get("quantity_to_make", 1)
    laterality = config.get("laterality", "bilateral")
    split = config.get("split", False)
    selected = config.get("selected", {}) or {}

    # 🔍 Extract all PTAV IDs from the configuration
    if laterality == "bilateral" and split:
        ptav_ids = [int(pid) for side in ("left", "right") for pid in selected.get(side, {}).keys()]
    else:
        ptav_ids = [int(pid) for pid in selected.keys() if str(pid).isdigit()]

    # 🔁 Check for matrix override
    matrix = env["price.matrix"].sudo()
    matrix_record = matrix.search([
        ("product_tmpl_id", "=", template.id),
        ("ptav_ids", "subset_of", ptav_ids),
    ], limit=1)

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
            # "from_matrix": True,
            "from_matrix": bool(matrix_price), 
        }

    # ⛳️ Fallback: manual price breakdown
    base_price = template.list_price or 0.0
    base_multiplier = 2 if laterality == "bilateral" else 1
    raw_base = base_price * base_multiplier

    ptavs = env["product.template.attribute.value"].sudo().browse(ptav_ids)
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

    discount_factor = get_partner_discount(env, partner, template)
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


# def compute_cpq_price_breakdown(env, order_line, config):
#     template = order_line.product_template_id
#     partner = order_line.order_id.partner_id
#     currency = order_line.currency_id or env.user.company_id.currency_id
#     currency = currency.ensure_one()

#     quantity = config.get("quantity_to_make", 1)
#     laterality = config.get("laterality", "bilateral")
#     split = config.get("split", False)
#     selected = config.get("selected", {}) or {}

#     if laterality == "bilateral" and split:
#         ptav_ids = [
#             int(pid)
#             for side in ("left", "right")
#             for pid in selected.get(side, {}).keys()
#             if str(pid).isdigit()
#         ]
#     else:
#         ptav_ids = [int(pid) for pid in selected.keys() if str(pid).isdigit()]

#     matrix_model = env["price.matrix"].sudo()
#     matrix_record = matrix_model.search([
#         ("product_tmpl_id", "=", template.id),
#         ("ptav_ids", "subset_of", ptav_ids),
#     ], limit=1)

#     if matrix_record:
#         price_per_unit = matrix_record.price_total
#         final_price = currency.round(price_per_unit * quantity)
#         return {
#             "base_price": 0.0,
#             "discount_factor": 1.0,
#             "quantity": quantity,
#             "laterality": laterality,
#             "split": split,
#             "left": 0.0,
#             "right": 0.0,
#             "extras_total": 0.0,
#             "subtotal": price_per_unit,
#             "final_price": final_price,
#             "total": final_price,
#             "from_matrix": True,
#         }

#     base_price = template.list_price or 0.0
#     ptavs = env["product.template.attribute.value"].sudo().browse(ptav_ids)
#     left_total = right_total = 0.0

#     for ptav in ptavs:
#         if laterality == "bilateral" and split:
#             if str(ptav.id) in selected.get("left", {}):
#                 left_total += ptav.price_extra
#             if str(ptav.id) in selected.get("right", {}):
#                 right_total += ptav.price_extra
#         elif laterality == "left":
#             left_total += ptav.price_extra
#         elif laterality == "right":
#             right_total += ptav.price_extra
#         elif laterality == "bilateral":
#             left_total += ptav.price_extra
#             right_total += ptav.price_extra

#     base_multiplier = 2 if laterality == "bilateral" else 1
#     raw_base = base_price * base_multiplier
#     discount_factor = get_partner_discount(env, partner, template)
#     discounted_base = raw_base * discount_factor

#     extras_total = left_total + right_total
#     subtotal = discounted_base + extras_total
#     final_price = currency.round(subtotal * quantity)

#     return {
#         "base_price": round(raw_base, 2),
#         "discount_factor": discount_factor,
#         "quantity": quantity,
#         "laterality": laterality,
#         "split": split,
#         "left": round(left_total * quantity, 2),
#         "right": round(right_total * quantity, 2),
#         "extras_total": round(extras_total * quantity, 2),
#         "subtotal": round(subtotal, 2),
#         "final_price": final_price,
#         "total": final_price,
#         "from_matrix": False,
#     }


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



