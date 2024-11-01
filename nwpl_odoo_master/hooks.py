import logging

logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Transfer existing weight values to weight_dummy after installation
    since now the weight field is computed
    """
    env.cr.execute("UPDATE product_product SET weight_dummy = weight")

def set_sale_price_on_variant(env, template_id=None):
    sql = """
        UPDATE product_product pp
        SET fix_price = pt.list_price + (
            SELECT COALESCE(SUM(ptav.price_extra), 0)
            FROM product_variant_combination pvc
            LEFT JOIN product_template_attribute_value ptav ON
                ptav.id = pvc.product_template_attribute_value_id
            WHERE pvc.product_product_id = pp.id
            AND ptav.product_tmpl_id = pt.id
        )
        FROM product_template pt
        WHERE pt.id = pp.product_tmpl_id
    """
    if template_id:
        sql += "AND pt.id = %s"
        env.cr.execute(sql, (template_id,))
    else:
        env.cr.execute(sql)