import json
from markupsafe import escape

def render_summary_html(env, sale_order, config):

    if sale_order is None:
        raise ValueError("Sale order is required to render the summary.")

    currency = sale_order.currency_id
    currency_symbol = currency.symbol or '$'

    def format_currency(amount):
        return f"{currency_symbol}{amount:,.2f}"

    def get_label(attr_id, value):
        try:
            attr = env['product.template.attribute.line'].browse(int(attr_id))
            if isinstance(value, str):
                return f"{escape(attr.attribute_id.name)}: {escape(value)}"
            value_record = env['product.attribute.value'].browse(int(value))
            if value_record.exists():
                return f"{escape(attr.attribute_id.name)}: {escape(value_record.name)}"
            else:
                return f"{escape(attr.attribute_id.name)}: {escape(str(value))}"
        except Exception:
            return f"{escape(str(attr_id))}: {escape(str(value))}"

    def format_selection(selection):
        if not selection:
            return "<em>No selections made.</em>"
        return "<ul>" + "".join(f"<li>{get_label(k, v)}</li>" for k, v in selection.items()) + "</ul>"

    laterality_label = config['laterality'].capitalize()
    quantity = config['quantity_to_make']
    split_mode = 'Yes' if config['split'] else 'No'

    body = f"""
    <p><strong>🦶 Laterality:</strong> {escape(laterality_label)}</p>
    <p><strong>Quantity to Make:</strong> {quantity}</p>
    <p><strong>Split Mode:</strong> {split_mode}</p>
    <p><strong>Selections:</strong></p>
    <ul>
    """

    if config['split']:
        body += f"<li><strong>Left:</strong> {format_selection(config['selected'].get('left', {}))}</li>"
        body += f"<li><strong>Right:</strong> {format_selection(config['selected'].get('right', {}))}</li>"
    else:
        body += f"<li>{format_selection(config['selected'])}</li>"

    body += f"""
    </ul>
    <hr/>
    <p><strong>💰 Price Summary:</strong></p>
    <ul>
        <li>💵 Left Total: {format_currency(config['left_price'])}</li>
        <li>💵 Right Total: {format_currency(config['right_price'])}</li>
        <li>📊 Combined Total: <strong>{format_currency(config['total_price'])}</strong></li>
    </ul>
    """

    # Optional: Debug dump
    if env.context.get('debug'):
        raw_config = json.dumps(config, indent=2)
        body += f"""
        <hr/>
        <details>
            <summary>🔍 Debug: Raw Configuration</summary>
            <pre>{escape(raw_config)}</pre>
        </details>
        """

    return body
