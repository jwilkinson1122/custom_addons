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
    # raise UserError(f"🧩 CPQ Debug Config:\n{json.dumps(config, indent=2)}")

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

    # ✅ Log parsed values
    _logger.info("🦶 [CPQ] Laterality: %s, Quantity: %d, Split: %s", laterality, quantity, split)
    _logger.info("🧩 [CPQ] Selections: %s", json.dumps(selections, indent=2))
    _logger.info("💰 [CPQ] Prices: Left: %.2f, Right: %.2f, Total: %.2f", left_price, right_price, total_price)

    # ✅ Laterality & Quantity
    if laterality == "Bilateral":
        lines.append(f"🦶🦶 <b>Laterality:</b> {laterality}<br/>")
    else:
        lines.append(f"🦶 <b>Laterality:</b> {laterality}<br/>")
    lines.append(f"📦 <b>Quantity to Make:</b> {quantity}<br/>")
    lines.append(f"🔀 <b>Split Mode:</b> {'Yes' if split else 'No'}<br/><br/>")

    # ✅ Selections
    if selections:
        lines.append("<b>Selections:</b><br/>")
        for attr_id, value in selections.items():
            lines.append(f"{value}<br/>")
        lines.append("<br/>")

    # ✅ Pricing Summary
    lines.append(f"<b>Price Summary:</b><br/>")
    lines.append(f"💵 Left Total: {format_currency(left_price, env)}<br/>")
    lines.append(f"💵 Right Total: {format_currency(right_price, env)}<br/>")
    lines.append(f"📊 Combined Total: {format_currency(total_price, env)}")

    html_output = "".join(lines)

    _logger.info("🖨️ [CPQ] Final Summary HTML:\n%s", html_output)
    _logger.info("💰 [CPQ] Price Breakdown: Left: %s, Right: %s, Total: %s",
                format_currency(left_price, env),
                format_currency(right_price, env),
                format_currency(total_price, env))


    return html_output


