import logging
from odoo.tools.sql import column_exists

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """Pre-init hook to add columns for computed fields on ir_attachment."""
    try:
        if column_exists(env.cr, "ir_attachment", "file_storage_id"):
            return

        _logger.info("Adding columns for computed fields on ir_attachment")

        env.cr.execute(
            """
            ALTER TABLE ir_attachment
            ADD COLUMN IF NOT EXISTS file_storage_id INTEGER;
        """
        )
        env.cr.execute(
            """
            ALTER TABLE ir_attachment
            ADD CONSTRAINT IF NOT EXISTS fk_ir_attachment_file_storage
            FOREIGN KEY (file_storage_id) REFERENCES file_storage(id);
        """
        )
        env.cr.execute(
            """
            ALTER TABLE ir_attachment
            ADD COLUMN IF NOT EXISTS file_url VARCHAR;
        """
        )
        env.cr.execute(
            """
            ALTER TABLE ir_attachment
            ADD COLUMN IF NOT EXISTS file_storage_code VARCHAR;
        """
        )

        _logger.info("Columns successfully added on ir_attachment")
        env.cr.commit()
    except Exception as e:
        env.cr.rollback()
        _logger.error(f"Error in pre_init_hook: {str(e)}")


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


def uninstall_hook(env):
    """
    Deletes System Parameters
    """
    env["ir.config_parameter"].sudo().search(
        [("key", "=", "nwpl_odoo_master.amazon_access_key")]
    ).unlink()
    env["ir.config_parameter"].sudo().search(
        [("key", "=", "nwpl_odoo_master.amazon_secret_key")]
    ).unlink()
    env["ir.config_parameter"].sudo().search(
        [("key", "=", "nwpl_odoo_master.amazon_bucket_name")]
    ).unlink()
    env["ir.config_parameter"].sudo().search(
        [("key", "=", "nwpl_odoo_master.amazon_connector")]
    ).unlink()
