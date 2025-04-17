import logging
import json
from markupsafe import Markup
from odoo.tools.safe_eval import json
from odoo.tools.translate import _
from odoo import _
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger(__name__)
# _logger = logging.getLogger("cpq")
# _logger.info("🧩 CPQ Step: %s", "something important")

def format_currency(amount, env):
    return formatLang(env, amount, currency_obj=env.user.company_id.currency_id)

def render_summary_html(env, order, config):
    laterality = config.get("laterality", "bilateral")
    split = config.get("split", False)
    selected = config.get("selected", {})
    quantity = config.get("quantity_to_make", 1)

    def get_name(ptav_id):
        ptav = env["product.template.attribute.value"].sudo().browse(int(ptav_id))
        return ptav.name if ptav.exists() else str(ptav_id)

    def get_price(ptav_id):
        ptav = env["product.template.attribute.value"].sudo().browse(int(ptav_id))
        return ptav.price_extra if ptav.exists() else 0.0

    def line(label, val, price=None):
        price_html = f"<span class='float-end text-muted'>+ ${price:.2f}</span>" if price else ""
        return f"<li>{label}: <b>{val}</b>{price_html}</li>"

    lines = []
    left_total = right_total = 0.0

    if laterality == "bilateral" and split:
        left = selected.get("left", {})
        right = selected.get("right", {})
        for attr_id in set(left.keys()).union(right.keys()):
            lval = get_name(attr_id) if attr_id in left else "-"
            rval = get_name(attr_id) if attr_id in right else "-"
            price = 0.0
            if attr_id in left:
                price += get_price(attr_id)
            if attr_id in right:
                price += get_price(attr_id)
            lines.append(f"<li>{attr_id}: <b>L:</b> {lval}, <b>R:</b> {rval} <span class='float-end text-muted'>+ ${price:.2f}</span></li>")
            left_total += get_price(attr_id) if attr_id in left else 0
            right_total += get_price(attr_id) if attr_id in right else 0

    else:
        side_label = {"left": "Left", "right": "Right", "bilateral": "Shared"}.get(laterality, "Shared")
        for attr_id, val in selected.items():
            name = get_name(attr_id)
            price = get_price(attr_id)
            lines.append(line(f"{side_label} - {name}", val, price))
            if laterality == "left":
                left_total += price
            elif laterality == "right":
                right_total += price
            elif laterality == "bilateral":
                left_total += price
                right_total += price

    base_price = order.product_id.product_tmpl_id.list_price
    base = base_price * (2 if laterality == "bilateral" else 1) * quantity
    extras = (left_total + right_total) * quantity
    total = base + extras

    pricing = f"""
    <li><b>💵 Base:</b> ${base:.2f}</li>
    <li><b>➕ Extras:</b> ${extras:.2f}</li>
    <li><b>📊 Total (x{quantity}):</b> <b>${total:.2f}</b></li>
    """

    return Markup(f"<ul>{''.join(lines)}<hr/>{pricing}</ul>")

# Current
# def render_summary_html(env, order, config, mode="html"):
#     if not config:
#         _logger.warning("⚠️ [CPQ] render_summary_html: Empty config provided.")
#         return "<i>No configuration</i>"

#     _logger.info("🖨️ [CPQ] render_summary_html called with config: %s", json.dumps(config, indent=2))

#     lines = []
#     laterality = config.get("laterality", "").capitalize()
#     quantity = config.get("quantity_to_make", 1)
#     split = config.get("split", False)

#     selections = config.get("selected", {})
#     left_price = config.get("left_price", 0.0)
#     right_price = config.get("right_price", 0.0)
#     total_price = config.get("total_price", 0.0)

#     ptav_ids = set()
#     if isinstance(selections, dict):
#         if split:
#             ptav_ids.update(int(k) for side in ("left", "right") for k in selections.get(side, {}) if k.isdigit())
#         else:
#             ptav_ids.update(int(k) for k in selections if k.isdigit())

#     ptav_by_id = {ptav.id: ptav for ptav in env["product.template.attribute.value"].browse(list(ptav_ids))}
#     attribute_by_id = {}
#     for ptav in ptav_by_id.values():
#         attribute_by_id.setdefault(ptav.attribute_id.id, ptav.attribute_id)

#     lines.append(f"🦶 {'🦶 ' if laterality == 'Bilateral' else ''}<b>Laterality:</b> {laterality}<br/>")
#     lines.append(f"📦 <b>Quantity to Make:</b> {quantity}<br/>")
#     lines.append(f"🔀 <b>Split Mode:</b> {'Yes' if split else 'No'}<br/><br/>")

#     if selections:
#         lines.append("<b>Selections:</b><br/>")

#         def render_side(side_name, side_selections):
#             result = []
#             for ptav_id_str, value in side_selections.items():
#                 ptav_id = int(ptav_id_str)
#                 ptav = ptav_by_id.get(ptav_id)
#                 if not ptav:
#                     continue
#                 attribute = ptav.attribute_id
#                 price_extra = ptav.price_extra or 0.0
#                 result.append(f"<span title='{attribute.name}'>{attribute.name}: <b>{ptav.name}</b>"
#                               f"{f' <small>({format_currency(price_extra, env)})</small>' if price_extra else ''}"
#                               f"</span><br/>")
#             return "".join(result)

#         if split:
#             left_selections = selections.get("left", {})
#             right_selections = selections.get("right", {})
#             attr_ids = set(
#                 int(ptav_id) for ptav_id in list(left_selections.keys()) + list(right_selections.keys())
#             )

#             for attr in attribute_by_id.values():
#                 left_val = None
#                 right_val = None
#                 for ptav_id, ptav in ptav_by_id.items():
#                     if ptav.attribute_id.id != attr.id:
#                         continue
#                     if str(ptav_id) in left_selections:
#                         left_val = ptav.name
#                     if str(ptav_id) in right_selections:
#                         right_val = ptav.name
#                 match = "✅" if left_val == right_val and left_val else "❌"
#                 lines.append(f"{attr.name}: {left_val or '-'} / {right_val or '-'} {match}<br/>")

#         else:
#             lines.append(render_side("Shared", selections))

#         lines.append("<br/>")

#     lines.append(f"<b>Price Summary:</b><br/>")
#     lines.append(f"💵 Left Total: {format_currency(left_price, env)}<br/>")
#     lines.append(f"💵 Right Total: {format_currency(right_price, env)}<br/>")
#     lines.append(f"📊 Combined Total: {format_currency(total_price, env)}")

#     html_output = "".join(lines)

#     _logger.info("🖨️ [CPQ] Final Summary HTML:\n%s", html_output)
#     return html_output

def render_summary_plaintext(env, order, config):
    html = render_summary_html(env, order, config)
    return Markup(html).striptags()

# def _calculate_total_extras(self, config):
#         selected = config.get('selected', {})
#         if not selected:
#             return 0

#         ptav_ids = [int(k) for k in selected if k.isdigit()]
#         ptavs = self.env['product.template.attribute.value'].browse(ptav_ids)

#         total_extra = sum(ptav.price_extra for ptav in ptavs)
#         _logger.info(f"🧩 Total extras calculated: {total_extra}")
#         return total_extra


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
    currency = order_line.currency_id

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
