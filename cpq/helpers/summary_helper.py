# -*- coding: utf-8 -*-
import logging
import json
from markupsafe import Markup
from odoo.tools.translate import _
from odoo import _
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError, ValidationError
from odoo.models import BaseModel

_logger = logging.getLogger(__name__)


def generate_cpq_qr_payload(order_id, line_id, template_id, config_hash=None, version=1):
    """
    Backend equivalent of generateCpqQrPayload from frontend utils.
    """
    uri = f"cpq://order/{order_id}/line/{line_id}/template/{template_id}"
    params = []
    if config_hash:
        params.append(f"config={config_hash}")
    if version:
        params.append(f"v={version}")
    if params:
        uri += f"?{'&'.join(params)}"
    return uri

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
    base_row = f"<li><b>💵 Base:</b> ${base_price:.2f} <span class='text-muted'>{breakdown_note}</span></li>"

    price_block = f"""
        <hr/>
        <ul class='mt-2 mb-0'>
            {'<li><b>🦶 Left Extras:</b> $%.2f</li>' % left_total if left_total else ''}
            {'<li><b>🦶 Right Extras:</b> $%.2f</li>' % right_total if right_total else ''}
            {base_row}
            <li><b>➕ Extras:</b> ${extras_total:.2f}</li>
            <li><b>📊 Total (x{quantity}):</b> <b>${total:.2f}</b></li>
        </ul>
    """

    return Markup(f"<div class='cpq-summary'>{''.join(lines)}{price_block}</div>")

def render_summary_plaintext(env, order, config):
    html = render_summary_html(env, order, config)
    return Markup(html).striptags()

def compute_cpq_price_breakdown(env, order_line, config):
    """
    Computes a full CPQ price breakdown based on laterality, split mode, and selected PTAVs.

    Returns:
        dict: {
            base_price: float,
            extras_total: float,
            discount_factor: float,
            quantity: int,
            subtotal: float,
            final_price: float,
            left: float,
            right: float,
            laterality: str,
            split: bool,
        }
    """
    template = order_line.product_template_id
    partner = order_line.order_id.partner_id
    # currency = order_line.currency_id

    currency = order_line.currency_id
    if not currency or not currency.ids:
        currency = env.user.company_id.currency_id
    currency = currency.ensure_one()


    base_price = template.list_price or 0.0
    quantity = config.get("quantity_to_make", 1)
    laterality = config.get("laterality", "bilateral")
    split = config.get("split", False)
    selected = config.get("selected", {}) or {}

    left_total = 0.0
    right_total = 0.0

    # 🔍 Get PTAVs from selection
    if laterality == "bilateral" and split:
        ptav_ids = [int(pid) for pid in list(selected.get("left", {}).keys()) + list(selected.get("right", {}).keys())]
    else:
        ptav_ids = [int(pid) for pid in selected.keys() if str(pid).isdigit()]

    ptavs = env["product.template.attribute.value"].sudo().browse(ptav_ids)

    for ptav in ptavs:
        if laterality == "bilateral" and split:
            if str(ptav.id) in selected.get("left", {}):
                left_total += ptav.price_extra
            if str(ptav.id) in selected.get("right", {}):
                right_total += ptav.price_extra
        elif laterality == "left":
            left_total += ptav.price_extra
        elif laterality == "right":
            right_total += ptav.price_extra
        elif laterality == "bilateral":
            # Shared bilateral
            left_total += ptav.price_extra
            right_total += ptav.price_extra

    # 🎯 Base price logic
    base_multiplier = 2 if laterality == "bilateral" else 1
    raw_base = base_price * base_multiplier

    # 💰 Apply discount (optional method)
    discount_factor = get_partner_discount(env, partner, template)  # e.g. 1.0 means no discount
    discounted_base = raw_base * discount_factor

    # 📊 Totals
    extras_total = (left_total + right_total)
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
        "total": final_price, # ✅ Add this alias to avoid KeyError in consumers
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



