import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    _logger.info("Running post-migration for version %s", version)

    # Fix invalid JSON or non-object values in section_data
    cr.execute(
        """
        UPDATE sale_order_wizard
        SET section_data = '{}'::jsonb
        WHERE section_data IS NULL
           OR section_data::text IN ('false', 'true', '', 'null')
           OR NOT jsonb_typeof(section_data::jsonb) = 'object';
        """
    )

    # Additional integrity check to ensure consistency
    cr.execute(
        """
        UPDATE sale_order_wizard
        SET section_data = '{}'::jsonb
        WHERE section_data IS NULL OR NOT jsonb_typeof(section_data) = 'object';
        """
    )

    _logger.info("Post-migration completed: section_data consistency ensured.")
