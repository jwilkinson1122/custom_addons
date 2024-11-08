import logging
from odoo.tools.sql import column_exists

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """Pre-init hook to add columns for computed fields on ir_attachment."""
    try:
        # Check if the column `file_storage_id` already exists to avoid duplicate creation.
        if column_exists(env.cr, "ir_attachment", "file_storage_id"):
            return  # columns already added; avoid duplicate modifications

        _logger.info("Adding columns for computed fields on ir_attachment")

        # Adding the required columns with necessary constraints
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
