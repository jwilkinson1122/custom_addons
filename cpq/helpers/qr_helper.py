import logging
from urllib.parse import urlparse, parse_qs
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

def parse_cpq_qr_payload(payload):
    """
    Parses CPQ QR code payloads of the form:
    cpq://order/{order_id}/line/{line_id}/template/{template_id}?config={hash}&v=1
    """
    result = {}
    if payload.startswith('cpq://'):
        payload = payload.replace('cpq://', 'https://')  # Hack: parse as standard URL

    parsed = urlparse(payload)
    path_parts = parsed.path.strip('/').split('/')

    try:
        if 'order' in path_parts:
            result['order_id'] = int(path_parts[path_parts.index('order') + 1])
        if 'line' in path_parts:
            result['line_id'] = int(path_parts[path_parts.index('line') + 1])
        if 'template' in path_parts:
            result['template_id'] = int(path_parts[path_parts.index('template') + 1])

        query = parse_qs(parsed.query)
        if 'config' in query:
            result['config_hash'] = query['config'][0]

    except (ValueError, IndexError) as e:
        _logger.error(f"❌ Failed to parse QR payload: {e}")
        raise UserError("Invalid QR code payload format.")

    return result

