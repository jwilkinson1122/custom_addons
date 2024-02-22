from odoo import SUPERUSER_ID, api
import logging

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """Init product variant name with product template name"""
    env.cr.execute(
        """
        UPDATE product_product pp
        SET name = pt.name
        FROM product_template pt
        WHERE pp.product_tmpl_id = pt.id;
        """
    )
