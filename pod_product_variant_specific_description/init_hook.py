from odoo import SUPERUSER_ID, api
import logging

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    _logger.info("Setting product variant description with product template description")
    env.cr.execute(
        """
        UPDATE product_product pp
        SET description = pt.description
        FROM product_template pt
        WHERE pp.product_tmpl_id = pt.id;
        """
    )