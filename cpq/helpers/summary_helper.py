import logging
from odoo import _
from markupsafe import Markup

from odoo.exceptions import UserError, ValidationError

import json
from odoo.tools.misc import formatLang

_logger = logging.getLogger(__name__)
_logger = logging.getLogger("cpq")
_logger.info("🧩 CPQ Step: %s", "something important")

def format_currency(amount, env):
    return formatLang(env, amount, currency_obj=env.user.company_id.currency_id)

# Current
def render_summary_html(env, order, config, mode="html"):
    if not config:
        _logger.warning("⚠️ [CPQ] render_summary_html: Empty config provided.")
        return "<i>No configuration</i>"

    _logger.info("🖨️ [CPQ] render_summary_html called with config: %s", json.dumps(config, indent=2))

    lines = []
    laterality = config.get("laterality", "").capitalize()
    quantity = config.get("quantity_to_make", 1)
    split = config.get("split", False)

    selections = config.get("selected", {})
    left_price = config.get("left_price", 0.0)
    right_price = config.get("right_price", 0.0)
    total_price = config.get("total_price", 0.0)

    # ✅ Prepare PTAV and Attribute mapping
    ptav_ids = set()
    if isinstance(selections, dict):
        if split:
            ptav_ids.update(int(k) for side in ("left", "right") for k in selections.get(side, {}) if k.isdigit())
        else:
            ptav_ids.update(int(k) for k in selections if k.isdigit())

    ptav_by_id = {ptav.id: ptav for ptav in env["product.template.attribute.value"].browse(list(ptav_ids))}
    attribute_by_id = {}
    for ptav in ptav_by_id.values():
        attribute_by_id.setdefault(ptav.attribute_id.id, ptav.attribute_id)

    # ✅ Summary header
    lines.append(f"🦶 {'🦶 ' if laterality == 'Bilateral' else ''}<b>Laterality:</b> {laterality}<br/>")
    lines.append(f"📦 <b>Quantity to Make:</b> {quantity}<br/>")
    lines.append(f"🔀 <b>Split Mode:</b> {'Yes' if split else 'No'}<br/><br/>")

    # ✅ Selections
    if selections:
        lines.append("<b>Selections:</b><br/>")

        def render_side(side_name, side_selections):
            result = []
            for ptav_id_str, value in side_selections.items():
                ptav_id = int(ptav_id_str)
                ptav = ptav_by_id.get(ptav_id)
                if not ptav:
                    continue
                attribute = ptav.attribute_id
                price_extra = ptav.price_extra or 0.0
                result.append(f"<span title='{attribute.name}'>{attribute.name}: <b>{ptav.name}</b>"
                              f"{f' <small>({format_currency(price_extra, env)})</small>' if price_extra else ''}"
                              f"</span><br/>")
            return "".join(result)

        if split:
            left_selections = selections.get("left", {})
            right_selections = selections.get("right", {})
            attr_ids = set(
                int(ptav_id) for ptav_id in list(left_selections.keys()) + list(right_selections.keys())
            )

            for attr in attribute_by_id.values():
                left_val = None
                right_val = None
                for ptav_id, ptav in ptav_by_id.items():
                    if ptav.attribute_id.id != attr.id:
                        continue
                    if str(ptav_id) in left_selections:
                        left_val = ptav.name
                    if str(ptav_id) in right_selections:
                        right_val = ptav.name
                match = "✅" if left_val == right_val and left_val else "❌"
                lines.append(f"{attr.name}: {left_val or '-'} / {right_val or '-'} {match}<br/>")

        else:
            lines.append(render_side("Shared", selections))

        lines.append("<br/>")

    # ✅ Pricing Summary
    lines.append(f"<b>Price Summary:</b><br/>")
    lines.append(f"💵 Left Total: {format_currency(left_price, env)}<br/>")
    lines.append(f"💵 Right Total: {format_currency(right_price, env)}<br/>")
    lines.append(f"📊 Combined Total: {format_currency(total_price, env)}")

    html_output = "".join(lines)

    _logger.info("🖨️ [CPQ] Final Summary HTML:\n%s", html_output)
    return html_output

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

#     _logger.info("🦶 [CPQ] Laterality: %s, Quantity: %d, Split: %s", laterality, quantity, split)
#     _logger.info("🧩 [CPQ] Selections: %s", json.dumps(selections, indent=2))
#     _logger.info("💰 [CPQ] Prices: Left: %.2f, Right: %.2f, Total: %.2f", left_price, right_price, total_price)

#     if laterality == "Bilateral":
#         lines.append(f"🦶🦶 <b>Laterality:</b> {laterality}<br/>")
#     else:
#         lines.append(f"🦶 <b>Laterality:</b> {laterality}<br/>")
#     lines.append(f"📦 <b>Quantity to Make:</b> {quantity}<br/>")
#     lines.append(f"🔀 <b>Split Mode:</b> {'Yes' if split else 'No'}<br/><br/>")

#     if selections:
#         lines.append("<b>Selections:</b><br/>")
#         for attr_id, value in selections.items():
#             lines.append(f"{value}<br/>")
#         lines.append("<br/>")

#     lines.append(f"<b>Price Summary:</b><br/>")
#     lines.append(f"💵 Left Total: {format_currency(left_price, env)}<br/>")
#     lines.append(f"💵 Right Total: {format_currency(right_price, env)}<br/>")
#     lines.append(f"📊 Combined Total: {format_currency(total_price, env)}")

#     html_output = "".join(lines)

#     _logger.info("🖨️ [CPQ] Final Summary HTML:\n%s", html_output)
#     _logger.info("💰 [CPQ] Price Breakdown: Left: %s, Right: %s, Total: %s",
#                 format_currency(left_price, env),
#                 format_currency(right_price, env),
#                 format_currency(total_price, env))


#     return html_output


