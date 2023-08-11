import logging
from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

try:
    from . import init_hooks
except ImportError:
    _logger.info("Cannot find module in addons path.")


def post_init_hook(cr, registry):
    init_hooks.post_init_hook(
        cr,
        "product.product_comp_rule",
        "product.template",
        # "base.res_partner_rule",
        # "res.partner",
    )


def uninstall_hook(cr, registry):
    init_hooks.uninstall_hook(
        cr,
        "product.product_comp_rule",
    )
