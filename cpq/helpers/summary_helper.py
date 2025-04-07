from odoo import _
from markupsafe import Markup


def render_summary_html(env, order, config):
    """ Render clean, readable configuration summary HTML """
    if not config:
        return "No configuration available."

    # Extract config data safely
    laterality = config.get("laterality", "unknown").capitalize()
    quantity = config.get("quantity_to_make", 1)
    split = config.get("split", False)

    selected = config.get("selected", {})
    if not isinstance(selected, dict):
        selected = {}

    price_left = config.get("left_price", 0)
    price_right = config.get("right_price", 0)
    price_total = config.get("total_price", 0)

    # Fetch PTAV names from IDs
    ptav_ids = [int(k) for k in selected.keys() if str(k).isdigit()]
    ptavs = env["product.template.attribute.value"].browse(ptav_ids)

    attr_value_map = {}
    for ptav in ptavs:
        attribute_name = ptav.attribute_id.name
        value_name = ptav.name
        attr_value_map[str(ptav.id)] = (attribute_name, value_name)

    # Start HTML summary
    html = f"""
    <div style="font-size: 13px; line-height: 1.4;">
        <div><strong>🦶 Laterality:</strong> {laterality}</div>
        <div><strong>Quantity to Make:</strong> {quantity}</div>
        <div><strong>Split Mode:</strong> {"Yes" if split else "No"}</div>
    """

    # Selections
    if attr_value_map:
        html += '<div><strong>Selections:</strong><br/>'
        for attr_name, value_name in attr_value_map.values():
            html += f'{attr_name}: {value_name}<br/>'
        html += '</div>'

    #     html += '<div><strong>Selections:</strong><ul style="margin: 4px 0; padding-left: 16px;">'
    #     for ptav_id, (attr_name, value_name) in attr_value_map.items():
    #         html += f'<li>{attr_name}: {value_name}</li>'
    #     html += '</ul></div>'
    # else:
    #     html += "<div><strong>Selections:</strong> None</div>"

    # Price Summary
    html += f"""
        <div style="margin-top: 8px;">
            <strong>💰 Price Summary:</strong><br/>
            💵 Left Total: {format_currency(env, order, price_left)}<br/>
            💵 Right Total: {format_currency(env, order, price_right)}<br/>
            📊 Combined Total: {format_currency(env, order, price_total)}<br/>
        </div>
    """

    # html += f"""
    #     <div style="margin-top: 8px;">
    #         <strong>💰 Price Summary:</strong>
    #         <ul style="margin: 4px 0; padding-left: 16px;">
    #             <li>💵 Left Total: {format_currency(env, order, price_left)}</li>
    #             <li>💵 Right Total: {format_currency(env, order, price_right)}</li>
    #             <li>📊 Combined Total: {format_currency(env, order, price_total)}</li>
    #         </ul>
    #     </div>
    # </div>
    # """

    return Markup(html)


def format_currency(env, order, amount):
    currency = order.currency_id or env.user.company_id.currency_id
    return currency.with_context(lang=order.partner_id.lang or env.user.lang).format(amount, currency)
